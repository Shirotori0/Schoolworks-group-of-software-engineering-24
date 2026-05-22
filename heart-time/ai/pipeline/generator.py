from .emotion import detect_emotion
from ..agent import agent
from ..prompt import prompt 
from ..rag.rag import retrieve_memory
from ..memory.memory import store_memory

#已停用
def generate_response(user_input: str, user_id: str) -> str:
    emotion = detect_emotion(user_input)

    memory = retrieve_memory(user_input, user_id=user_id)
    
    prompt.user_input = user_input
    prompt.emotion = emotion
    prompt.memory = memory
    
    response = agent.chat(messages=[{"role": "user", "content": prompt.build_prompt()}])
    
    store_memory(user_input, user_id=user_id) #待完善

    
    return response

from .runtime import AIRuntime
from ..tools import toolRegistry
def generate_runtime(session_id: str = None):
    runtime = AIRuntime(
        agent=agent,
        prompt=prompt,
        tool_registry=toolRegistry,
        session_id=session_id
    )
    return runtime

