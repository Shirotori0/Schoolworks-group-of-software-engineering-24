from ..prompt import build_prompt 
def generate_response(user_input: str, emotion, memory):
    prompt = build_prompt(
        user_input, 
        emotion, 
        memory)
    response = call_llm(prompt)
    return response