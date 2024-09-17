import torch
import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer
import bitsandbytes as bnb  # For quantization

class CommentSummarizer:
    def __init__(self, model_name, chat_file_path, device="cuda:0"):
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, 
            load_in_8bit=True,  # 8-bit quantization
            device_map='auto',  # Automatically selects the device (GPU)
        )
        self.file_path = chat_file_path

    def load_chat(self):
        data = pd.read_csv(self.file_path)
        comments = data['댓글 내용'].tolist()
        return comments

    def summarize(self, prompt_template, max_length=5000, temperature=0.7):
        comments = self.load_chat()
        # 입력 프롬프트 설정
        prompt = prompt_template.format(comments=comments)
        input_ids = self.tokenizer.encode(prompt, return_tensors='pt').to(self.device)
        
        # 텍스트 생성
        with torch.no_grad():
            output = self.model.generate(input_ids, max_length=max_length, do_sample=True, temperature=temperature)
        
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return generated_text

# Test
if __name__ == "__main__":
    model_name = "rtzr/ko-gemma-2-9b-it"
    file_path = './data/news_mudo_yt.csv'

    # CommentSummarizer 클래스 인스턴스 생성
    summarizer = CommentSummarizer(model_name=model_name, chat_file_path=file_path)

    # 입력 프롬프트
    prompt_template = "{comments} 이건 유튜브 라이브채팅 댓글이야. 어떤 주제를 가지고 얘기를 하고 있고, 대화의 흐름을 파악해서 주제를 3줄로 요약해줘."

    # 요약 생성
    summary = summarizer.summarize(prompt_template)
    print("=== 요약 결과 ===")
    print(summary)
