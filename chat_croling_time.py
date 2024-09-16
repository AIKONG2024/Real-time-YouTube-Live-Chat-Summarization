import pytchat
import pafy
import pandas as pd
import time  
from dotenv import load_dotenv
import os

# 환경 변수에서 API 키 로드
load_dotenv()
api_key = os.getenv('YOUTUBE_API_KEY')

os.environ['PAFY_BACKEND'] = 'yt-dlp'
pafy.set_api_key(api_key)

collection_time = 600 #댓글 수집 시간 (sec)

video_id = 'w3YN5dH1JaQ'  # 채널 ID
channel_name = 'mudo'  # 채널명
file_path = f"./data/news_{channel_name}_yt.csv"

# 비디오 정보 가져오기
video = pafy.new(video_id)
print(video.title)

# CSV 파일이 없으면 생성
if not os.path.exists(file_path):
    empty_df = pd.DataFrame(columns=['제목', '채널 명', '스트리밍 시작 시간', '댓글 작성자', '댓글 내용', '댓글 작성 시간'])
    empty_df.to_csv(file_path, index=False, encoding='utf-8-sig')

# 채팅 인스턴스 생성
chat = pytchat.create(video_id=video_id)

# 시작 시간 기록
start_time = time.time()

while chat.is_alive():
    try:
        current_time = time.time()
        elapsed_time = current_time - start_time  # 경과 시간 계산

        # 1분(60초)이 지나면 루프 종료
        if elapsed_time >= collection_time:
            break

        data = chat.get()
        items = data.items
        for c in items:
            print(f" {c.datetime} [{c.author.name}] - {c.message}")
            df = {
                '제목': [video.title],
                '채널 명': [video.author],
                '스트리밍 시작 시간': [video.published],
                '댓글 작성자': [c.author.name],
                '댓글 내용': [c.message],
                '댓글 작성 시간': [c.datetime]
            }

            result = pd.DataFrame(df)
            result.to_csv(file_path, mode='a', header=False, index=False, encoding='utf-8-sig')

    except KeyboardInterrupt:
        chat.terminate()
        break
    except Exception as e:
        print(f"Error while processing chat data: {e}")
        break

# CSV 파일 읽기 및 상위 30개 행 출력
df = pd.read_csv(file_path, names=['제목', '채널명', '스트리밍 시작 시간', '댓글 작성자', '댓글 내용', '댓글 작성 시간'], encoding='utf-8-sig')
print(df.head(30))
