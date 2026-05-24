from ..agent import agent
from ..prompt import prompt 
from ..memory.memory import store_memory



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

