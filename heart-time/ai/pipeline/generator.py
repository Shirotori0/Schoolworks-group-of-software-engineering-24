from ..agent import agent
from ..prompt import prompt 



from .runtime import AIRuntime
from ..tools import toolRegistry
def generate_runtime(session_id: str, script_path: str = None):
    runtime = AIRuntime(
        agent=agent,
        prompt=prompt,
        tool_registry=toolRegistry,
        session_id=session_id,
        script_path=script_path
    )
    return runtime

