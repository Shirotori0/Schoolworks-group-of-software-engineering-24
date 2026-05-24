from .tools import UpdateMemoryTool, UpdateSessionSummaryTool, UpdateEmotionTool, RetrieveContextTool, MakeScriptTool

class ToolRegistry:
    def __init__(self):
        self.tools = {
            UpdateMemoryTool.name: UpdateMemoryTool(),
            UpdateSessionSummaryTool.name: UpdateSessionSummaryTool(),
            UpdateEmotionTool.name: UpdateEmotionTool(),
            RetrieveContextTool.name: RetrieveContextTool(),
            MakeScriptTool.name: MakeScriptTool()
        }
        

    def execute_tool(self, tool_name, **kwargs):
        
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        return tool.execute(**kwargs)
    
    def get_tools(self):
        
        result = []
        for tool in self.tools.values():
            result.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            })
        return result