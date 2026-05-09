from .emotion import detect_emotion
from ..agent import agent
from ..prompt.prompt import build_prompt 
from .rag import retrieve_memory
from ..memory.memory import store_memory

def generate_response(user_input: str, user_id: str) -> str:
    emotion = detect_emotion(user_input)

    memory = retrieve_memory(user_input, user_id=user_id)
    
    prompt = build_prompt(
        user_input, 
        emotion, 
        memory)
    
    response = agent.chat(messages=[{"role": "user", "content": prompt}])
    
    store_memory(user_input, user_id=user_id) #待完善

    
    return response

