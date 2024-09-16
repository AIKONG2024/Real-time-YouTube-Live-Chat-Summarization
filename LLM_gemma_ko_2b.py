import torch
import pandas as pd
from transformers import pipeline

# 모델 로드
pipe = pipeline("text-generation", model="beomi/gemma-ko-2b", device=0) #GPU 사용, float16로 메모리 최적화

file_path = './data/news_mudo_yt.csv'
data = pd.read_csv(file_path)
comments = data['댓글 내용'].tolist()

# 사용자 입력에 따른 메시지
messages = [
    {"role": "summarization", "content": f"{comments} 를 3줄로 요약해줘."}
]

# 텍스트 생성
for message in messages:
    prompt = message["content"]
    response = pipe(prompt, max_length=2000, do_sample=True, temperature=0.7)
    print(response[0]["generated_text"])
    
