import time
import json

from fastapi import APIRouter

from domain.chatbot.reqeust_schema import ChatbotSchema
from lang_agency_prototype import chatbots

router = APIRouter(
    prefix="/api/chatbot",
)

@router.get("/hello", tags=["hello"])
async def hello():
    return {"content": "Hello World!"}

@router.post("/test_conversation", tags=["conversation"])
async def test_chat(chatbot_schema: ChatbotSchema):
    content = "챗봇이 궁시렁궁시렁 말을 했다!"
    task = "schedule_register"
    data = "Very important data"
    print(chatbot_schema.content)
    
    # 별도로 status(bool)
    if "까망" in chatbot_schema.content:
        content = "까망이가 궁시렁궁시렁 말을 했다!"
        time.sleep(10)
    
    return {
        "island_id": chatbot_schema.island_id, 
        "answer": content,
        "task": task,
        "data": {
            "year": 2023, 
            "month": 10, 
            "date": 24, 
            "hour": 20, 
            "minute": 0, 
            "content": "저녁식사 예약"
        }
    }
    
@router.post("/conversation", tags=["conversation"])
async def chat(chatbot_schema: ChatbotSchema):
    answer = chatbots.llm_chain.predict(input=chatbot_schema.content)
    answer["island_id"] = chatbot_schema.island_id
    return json.loads(answer)