# Real-time YouTube Live Chat Summarization
![제목-없는-디자인_cropped](https://github.com/user-attachments/assets/d839b14b-cdb3-40e4-b57b-9f9b55bcea00)

1. **Enter the Video ID of the YouTube Live chat and Input the chat collection duration**
2. **The summary will repeat continuously**
3. **Chat results and summary outcomes are displayed, and a graph shows positive/negative sentiment based on the chat atmosphere**
4. **If the sentiment is positive, the summary result will blink blue; if negative, it will blink red**
5. **It can check the summary history by clicking on "View History.**
   
## Project Description
The project aims to develop a system that can summarize real-time YouTube live chat.  
With YouTube live streams becoming increasingly popular, managing and understanding fast-paced live chats can be challenging.  
This project will focus on creating a solution that filters, organizes, and summarizes key points from the chat in real time.  
The summary will help viewers and moderators quickly capture the main discussions, highlight important messages, and minimize noise from irrelevant or repetitive comments. 

## Version
cuda version: 11.8  
cudnn version : 9.0.0  
python version : 3.11.9  

## Getting Started
1. **Clone Repository**

   ```bash
   git clone https://github.com/AIKONG2024/Real-time-YouTube-Live-Chat-Summarization.git
2. **Pip install**

   ```bash
   pip install -r requirements.txt  
4. **Run**  

   ```bash
   python app.py
   #I performed inference using a 4090 GPU. Systems with lower performance may not be able to run this.

##  Used LLM Model
  Gemma1,2 Korean Fine-tunning Models  
  
  **rtzr/ko-gemma-2-9b-it(https://huggingface.co/rtzr/ko-gemma-2-9b-it)**  
  **beomi/gemma-ko-2b(https://huggingface.co/beomi/gemma-ko-2b)**
