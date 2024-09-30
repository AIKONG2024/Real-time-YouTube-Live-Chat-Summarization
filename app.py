from flask import Flask, render_template, request, redirect, url_for, jsonify
from dotenv import load_dotenv
import os
import threading
from chat_crawler import Chat_Crawler  # 채팅 크롤링 클래스
from summarizer import CommentSummarizer  # 요약 클래스
import time
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# .env 파일에서 API 키 로드
load_dotenv()
api_key = os.getenv('YOUTUBE_API_KEY')

# 모델을 애플리케이션 시작 시 전역 변수로 로드
model_name = "rtzr/ko-gemma-2-9b-it"
summarizer = CommentSummarizer(model_name=model_name)

# 공유 데이터와 락 초기화
summarizing_status = {}
result_dict = {}
chat_contents = {}
video_info_dict = {}  # 비디오 정보 저장
history = []
status_lock = threading.Lock()
data_lock = threading.Lock()

def run_summarizer(session_id, video_id, collect_time, prompt_template):
    try:
        with status_lock:
            summarizing_status[session_id] = True

        # 채팅 크롤링 및 비디오 정보 가져오기
        print("=== 채팅 크롤링 시작 ===")
        crawler = Chat_Crawler(
            collect_time=collect_time,
            youtube_api_key=api_key,
            video_id=video_id
        )

        # 비디오 정보는 한 번만 가져옴
        if session_id not in video_info_dict:
            video_info = crawler.get_video()
            video_info_dict[session_id] = {
                "video_title": video_info.title,
                "video_author": video_info.author,
                "video_published": video_info.published
            }
        else:
            video_info = video_info_dict[session_id]

        # 채팅 크롤링 수행
        crawler.do_crawling()
        print("=== 채팅 크롤링 완료 ===")

        # 채팅 파일 경로 설정
        chat_file_path = f'./data/{video_id}_chat.csv'

        # 크롤링한 채팅 내용을 저장
        with open(chat_file_path, 'r', encoding='utf-8') as f:
            chat_content = f.read()

        # 채팅 내용 저장
        with data_lock:
            chat_contents[session_id] = chat_content
            result_dict[session_id] = {"summary": ""}

        # summarizer에 chat_file_path 설정
        summarizer.set_chat_file_path(chat_file_path)

        # 요약 결과 생성
        print("=== 요약 생성 시작 ===")
        def should_stop():
            with status_lock:
                return not summarizing_status.get(session_id, False)
        summary_result = summarizer.summarize(prompt_template, should_stop=should_stop)
        print("=== 요약 생성 완료 ===")

        # 요약 결과 저장
        with data_lock:
            result_dict[session_id]["summary"] = summary_result
            history.append(summary_result)

        # 상태 확인 후 대기
        wait_time = 0
        while wait_time < collect_time:
            with status_lock:
                if not summarizing_status.get(session_id, False):
                    break
            time.sleep(1)
            wait_time += 1

    except Exception as e:
        print(f"에러 발생: {str(e)}")
        with data_lock:
            result_dict[session_id] = {"summary": f"에러 발생: {str(e)}"}
    finally:
        with status_lock:
            summarizing_status[session_id] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_summary():
    # 폼 데이터 가져오기
    video_id = request.form['video_id']
    collect_time = int(request.form['collect_time'])

    # 세션 ID 생성
    session_id = str(uuid.uuid4())

    # 입력 프롬프트 생성
    prompt_template = """{comments}

위의 유튜브 라이브 채팅 댓글을 읽고, 주제와 대화의 흐름을 파악하여 아래의 형식으로 부드럽고 친근한 어조로 존댓말로 요약해줘:

1. 첫 번째 요약 내용
2. 두 번째 요약 내용
3. 세 번째 요약 내용

요약 예시: 
1. 시청자들은 스트리밍 중 게스트 등장에 신기해 합니다.
2. 시청자들은 스트리머의 시간을 끌고 고민하는 모습이 지루합니다.
3. 시청자들은 게스트들의 대화 내용이 너무 재미있습니다.

긍정:XX/부정:XX

- 위의 형식에 맞춰 요약 내용을 작성해 주고, 흐름을 이해할 수 있을 정도의 구체적인 키워드를 포함해줘.
- 요약 시 부드럽고 자연스러운 표현을 사용해줘.
- 긍정과 부정의 비율은 전체 100%를 기준으로 계산해줘.
- 다른 불필요한 말은 생략하고, 위의 형식으로만 출력해줘.
"""

    # 요약 작업을 별도의 스레드에서 실행
    summarizer_thread = threading.Thread(
        target=run_summarizer,
        args=(session_id, video_id, collect_time, prompt_template)
    )
    summarizer_thread.start()

    # 결과 페이지로 리디렉션 (session_id와 collect_time을 URL 파라미터로 전달)
    return redirect(url_for('summary', session_id=session_id, collect_time=collect_time))

@app.route('/summary')
def summary():
    session_id = request.args.get('session_id')
    collect_time = request.args.get('collect_time')
    with data_lock:
        video_info = video_info_dict.get(session_id, {
            'video_title': ' ',
            'video_author': ' ',
            'video_published': ' '
        })
        summary_result = result_dict.get(session_id, {}).get('summary', '')

    return render_template('summary.html', 
        session_id=session_id, 
        collect_time=collect_time, 
        video_title=video_info['video_title'], 
        video_author=video_info['video_author'], 
        video_published=video_info['video_published'],
        summary_result=summary_result
    )

@app.route('/update_video_info', methods=['POST'])
def update_video_info():
    session_id = request.json.get('session_id')
    with data_lock:
        video_info = video_info_dict.get(session_id, {})
    return jsonify(video_info)

@app.route('/stop', methods=['POST'])
def stop_summary():
    session_id = request.json.get('session_id')
    with status_lock:
        if session_id in summarizing_status:
            summarizing_status[session_id] = False
    return jsonify({'status': 'stopped'})

@app.route('/update_summary', methods=['POST'])
def update_summary():
    session_id = request.json.get('session_id')
    with data_lock:
        summary_result = result_dict.get(session_id, {}).get("summary", "")
    return jsonify({'summary': summary_result})

@app.route('/get_chat', methods=['POST'])
def get_chat():
    session_id = request.json.get('session_id')
    with data_lock:
        chat_content = chat_contents.get(session_id, '')
    return jsonify({'chat': chat_content})

@app.route('/is_summarizing', methods=['POST'])
def is_summarizing():
    session_id = request.json.get('session_id')
    with status_lock:
        is_summarizing = summarizing_status.get(session_id, False)
    return jsonify({'is_summarizing': is_summarizing})

@app.route('/history')
def view_history():
    with data_lock:
        return render_template('history.html', history=history)

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
