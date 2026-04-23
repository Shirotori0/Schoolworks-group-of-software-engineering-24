from ..prompt import build_prompt 
from .emotion import detect_emotion
from .rag import retrieve_memory
def generate_response(user_input: str):
    emotion = detect_emotion(user_input)
    memory = retrieve_memory(user_input, user_id="user1")
    
    prompt = build_prompt(
        user_input, 
        emotion, 
        memory)
    response = call_llm(prompt)
    return response