from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
from chat_crawler import Chat_Crawler  # 채팅 크롤링 클래스
from summarizer import CommentSummarizer  # 댓글 요약 클래스
import multiprocessing

app = Flask(__name__)

# .env 파일에서 API 키 로드
load_dotenv()
api_key = os.getenv('YOUTUBE_API_KEY')

# 별도의 프로세스에서 summarizer 실행을 위한 함수
def run_summarizer(video_id, channel_name, collect_time, conn):
    try:
        # Step 1: 채팅 크롤링
        crawler = Chat_Crawler(collect_time=collect_time, youtube_api_key=api_key, video_id=video_id, channel_name=channel_name)
        crawler.do_crawling()

        # Step 2: 댓글 요약
        model_name = "rtzr/ko-gemma-2-9b-it"
        chat_file_path = f'./data/news_{channel_name}_yt.csv'

        summarizer = CommentSummarizer(model_name=model_name, chat_file_path=chat_file_path)

        # 입력 프롬프트 생성
        prompt_template = """{comments} 이건 유튜브 라이브채팅 댓글이야. 
        주제와 댓글 시간 흐름을 참고해서 채팅 내용을 간결하게 3줄로 요약해줘.
        요약 예시는 
        "1. 시청자들은 스트리밍 중 게스트 등장에 신기해함.
        2. 시청자들은 스트리머의 시간을 끌고 고민하는 모습이 지루함.
        3. 시청자들은 게스트들의 대화 내용이 너무 재미있음." 형태로 출력해줘. 다만, 구체적인 내용은 예시를 따르지 말고 형태만 따라줘. 
        그리고 긍정적인 댓글 비율과 부정적인 댓글 비율을 100%을 기준으로 나눠서 출력해줘.
        출력 예시는
        "긍정:80/부정:20"
        이런식으로 출력해줘.
        """
        
        # 요약 결과 생성
        summary_result = summarizer.summarize(prompt_template)
        
        # 결과를 파이프로 전송
        conn.send(summary_result)
    finally:
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_summary():
    # 폼 데이터 가져오기
    video_id = request.form['video_id']
    channel_name = request.form['channel_name']
    collect_time = int(request.form['collect_time'])

    # Pipe 생성 (부모-자식 프로세스 간 통신)
    parent_conn, child_conn = multiprocessing.Pipe()

    # run_summarizer를 별도의 프로세스로 실행
    # process = multiprocessing.Process(target=run_summarizer, args=(video_id, channel_name, collect_time, child_conn))
    process.start()

    # 요약 결과 수신
    summary_result = parent_conn.recv()

    # 프로세스가 끝날 때까지 대기
    process.join()

    # 요약 결과 렌더링
    return render_template('result.html', summary_result=summary_result, message="요약이 완료되었습니다.")


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
