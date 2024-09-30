import pafy.backend_internal
import pafy.backend_youtube_dl
import pytchat
import pafy
import pandas as pd
import time
import os
from tqdm import tqdm 

class Chat_Crawler:
    def __init__(self, collect_time, youtube_api_key, video_id):
        self.collect_time = collect_time  # 댓글 수집 시간 (초)
        self.youtube_api_key = youtube_api_key
        self.video_id = video_id
        self.file_path = f"./data/{video_id}_chat.csv"

        os.environ['PAFY_BACKEND'] = 'yt-dlp'
        pafy.set_api_key(self.youtube_api_key)

    def get_video(self):
        video = pafy.new(self.video_id)
        return video

    def __create_chat_instance(self):
        return pytchat.create(video_id=self.video_id, interruptable=False)

    def __remove_existing_file(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
            print(f"기존 파일 {self.file_path} 삭제 완료.")
        else:
            print(f"삭제할 파일이 없습니다: {self.file_path}")

    def do_crawling(self):

        # 기존 파일이 있을 경우 삭제
        self.__remove_existing_file()

        # CSV 파일 새로 생성
        empty_df = pd.DataFrame(columns=['댓글 작성자', '댓글 내용', '댓글 작성 시간'])
        empty_df.to_csv(self.file_path, index=False, encoding='utf-8-sig')

        # 채팅 인스턴스 생성
        chat = self.__create_chat_instance()

        # 시작 시간 기록
        start_time = time.time()

        # tqdm - croling 진행 프로그래스바로 시각화
        with tqdm(total=self.collect_time, desc="crawling 진행 중", unit="초", bar_format="{l_bar}{bar}| {remaining}") as pbar:
            while chat.is_alive():
                try:
                    current_time = time.time()
                    elapsed_time = current_time - start_time  # 경과 시간 계산

                    # 수집 시간이 지나면 루프 종료
                    if elapsed_time >= self.collect_time:
                        break

                    data = chat.get()
                    items = data.items
                    for c in items:
                        df = {
                            '댓글 작성자': [c.author.name],
                            '댓글 내용': [c.message],
                            '댓글 작성 시간': [c.datetime]
                        }

                        result = pd.DataFrame(df)
                        result.to_csv(self.file_path, mode='a', header=False, index=False, encoding='utf-8-sig')
                    
                    # 경과 시간만큼 프로그래스바 갱신
                    pbar.update(current_time - start_time - pbar.n)

                except KeyboardInterrupt:
                    chat.terminate()
                    print("crawling 오류")
                    break
                except Exception as e:
                    chat.terminate()
                    print("crawling 오류")
                    print(f"Error while processing chat data: {e}")
                    break
        print("-crawling 완료-")
        
#Test
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    croling_instance = Chat_Crawler(collect_time=10, youtube_api_key=api_key, video_id="w3YN5dH1JaQ", channel_name="mudo")
    croling_instance.do_crawling()
