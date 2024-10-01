import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class CommentSummarizer:
    def __init__(self, model_name):
        # 모델과 토크나이저 초기화
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, 
            load_in_8bit=True,  # 8-bit quantization
            device_map='auto',  # Automatically selects the device (GPU)
        )
        self.chat_file_path = None

    def set_chat_file_path(self, chat_file_path):
        self.chat_file_path = chat_file_path

    def __load_chat(self):
        # 채팅 데이터를 로드하고 전처리
        if self.chat_file_path:
            with open(self.chat_file_path, 'r', encoding='utf-8') as f:
                comments = f.read()
            return comments
        else:
            return ""

    def summarize(self, prompt_template, should_stop=None, max_length=500, temperature=0.7):
        comments = self.__load_chat()
        prompt = prompt_template.format(comments=comments)
        input_ids = self.tokenizer.encode(prompt, return_tensors='pt').to(self.device)
        prompt_length = input_ids.shape[-1]

        # 텍스트 생성 설정
        generate_kwargs = {
            'input_ids': input_ids,
            'max_length': prompt_length + max_length,
            'do_sample': True,
            'temperature': temperature,
            'pad_token_id': self.tokenizer.eos_token_id,
        }

        # 생성 진행 중에 중단 여부 확인
        output = input_ids
        try:
            with torch.no_grad():
                for _ in range(0, max_length, 50):  # 50 토큰씩 생성
                    if should_stop and should_stop():
                        print("요약 작업 중단됨")
                        return "요약 작업이 중단되었습니다."
                    output = self.model.generate(
                        input_ids=output,
                        max_length=output.shape[1] + 50,
                        do_sample=True,
                        temperature=temperature,
                        pad_token_id=self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                    )
        except Exception as e:
            print(f"요약 중 에러 발생: {str(e)}")
            return f"요약 중 에러 발생: {str(e)}"

        generated_tokens = output[0, prompt_length:]
        generated_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        
        # 긍정 및 부정 비율 추출
        positive_ratio, negative_ratio = self.extract_sentiment(generated_text)

        # 요약 내용과 긍정/부정 비율 반환
        return generated_text.strip(), positive_ratio, negative_ratio

    def extract_sentiment(self, generated_text):
        # "긍정:XX/부정:XX" 형식의 데이터 추출
        print(generated_text)
        
        # 맨 뒤의 공백 제거
        generated_text = generated_text.strip()

        positive_ratio = 0
        negative_ratio = 0

        # 마지막 줄에서 긍정/부정 비율 추출
        sentiment_info = generated_text.split("\n")[-1]  # 가장 마지막 줄 추출
        
        try:
            # 긍정과 부정 비율 추출
            if "긍정:" in sentiment_info and "부정:" in sentiment_info:
                # 긍정 다음의 숫자 추출
                positive_ratio = int(sentiment_info.split("긍정:")[1].split("/")[0].strip().replace('%', ''))
                # 부정 다음의 숫자 추출
                negative_ratio = int(sentiment_info.split("부정:")[1].strip().replace('%', ''))
        except (ValueError, IndexError):
            print("긍정 및 부정 비율을 추출하는 데 오류가 발생했습니다.")

        return positive_ratio, negative_ratio

