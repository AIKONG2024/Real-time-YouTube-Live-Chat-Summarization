import pytchat
import pafy
import pandas as pd
from dotenv import load_dotenv
import os

# Load the environment variables from the .env file
load_dotenv()
api_key = os.getenv('API_KEY')

# Set the pafy backend to 'yt-dlp' and configure the API key
os.environ['PAFY_BACKEND'] = 'yt-dlp'
pafy.set_api_key(api_key)

video_id = 'FJfwehhzIhw' #YTN 채널
file_path = "./news_ytn_yt.csv"

video = pafy.new(video_id)
print(video.title)

if not os.path.exists(file_path):
    empty_df = pd.DataFrame(columns=['제목', '채널 명', '스트리밍 시작 시간', '댓글 작성자', '댓글 내용', '댓글 작성 시간'])
    empty_df.to_csv(file_path, index=False, encoding='utf-8-sig')

# Create a chat instance
chat = pytchat.create(video_id=video_id)

cnt = 0
while chat.is_alive():
    try:
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
        cnt += 1
        if cnt == 2000:
            break
    except KeyboardInterrupt:
        chat.terminate()
        break
    except Exception as e:
        print(f"Error while processing chat data: {e}")
        break

# Read the CSV file and display the first 30 rows
df = pd.read_csv(file_path, names=['제목', '채널명', '스트리밍 시작 시간', '댓글 작성자', '댓글 내용', '댓글 작성 시간'], encoding='utf-8-sig')
print(df.head(30))
