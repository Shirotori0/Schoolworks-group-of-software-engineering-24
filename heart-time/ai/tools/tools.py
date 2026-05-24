import json
from .base_tool import BaseTool

from ..prompt import prompt
class UpdateMemoryTool(BaseTool):
    name = "Update_Memory"
    description = "更新长期记忆，确保AI能够记住重要信息并在未来的对话中使用它。"

    parameters = {
        "type": "object",
        "properties": {
            "new_memory": {
                "type": "string",
                "description": "加入新的长期记忆内容，格式为{""标签"": ""内容""}，例如：{""长期稳定人格特征"": ""内向""}，{""长期情绪模式"": ""经常感到焦虑""}，{""长期偏好"": ""喜欢安静的环境""}，{""长期困扰"": ""人际关系问题""}"
            }
        },
        "required": ["new_memory"]

    }
    def execute(self, new_memory):
        # 这里可以添加逻辑来更新长期记忆，例如将新的记忆存储到数据库或内存中
        prompt.update_memory(new_memory)

        return "成功更新长期记忆"
        

class UpdateSessionSummaryTool(BaseTool):
    name = "Update_Session_Summary"
    description = "更新会话总结，确保AI能够跟踪对话的主题和进展。"

    parameters = {
        "type": "object",
        "properties": {
            "new_summary": {
                "type": "string",
                "description": "新的当前会话总结内容"
            }
        },
        "required": ["new_summary"]

    }
    def execute(self, new_summary):
        # 这里可以添加逻辑来更新会话总结，例如将新的总结存储到数据库或内存中
        prompt.update_session_summary(new_summary)

        return "会话总结已更新"
    
class UpdateEmotionTool(BaseTool):
    name = "Update_Emotion"
    description = "更新当前会话的的情绪，确保AI能够适应当前的环境。"

    parameters = {
        "type": "object",
        "properties": {
            "label": {
                "type": "string",
                "description": "新的的情绪标签，例如：happy, sad, angry, fearful, neutral, anxious, excited, frustrated, etc."
            },
            "score": {
                "type": "number",
                "description": "新的的情绪得分，范围在0到1之间"
            }
        },
        "required": ["label", "score"]
    }

    def execute(self, label, score):
        # 这里可以添加逻辑来更新当前会话的情绪，例如将新的的情绪标签和得分存储到数据库或内存中
        prompt.update_emotion_curve(label, score)

        return "当前会话的情绪已更新"
    
from ..rag.rag import retrieve_context
class RetrieveContextTool(BaseTool):
    name = "Retrieve_Context"
    description = "检索相关的上下文信息，确保AI能够获取必要的信息来生成更准确的回复。"

    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "检索上下文信息的查询语句"
            }
        },
        "required": ["query"]
    }

    def execute(self, query):
        # 这里可以添加逻辑来检索相关的上下文信息，例如从数据库或内存中获取与查询相关的信息
        retrieved_info = retrieve_context(query)

        return retrieved_info
    
from ..prompt.script import save_script
class MakeScriptTool(BaseTool):
    name = "Make_Script"
    description = "生成角色互动脚本，确保AI能够生成符合角色设定的回复。"

    parameters = {
        "type": "object",
        "properties": {
        "name": {
          "type": "string",
          "description": "角色名字"
        },
        "age": {
          "type": "integer",
          "description": "角色年龄"
        },
        "gender": {
          "type": "string",
          "enum": ["male", "female", "other"],
          "description": "角色性别"
        },
        "occupation": {
          "type": "string",
          "description": "角色职业"
        },
        "background": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "角色背景经历"
        },
        "personality": {
          "type": "object",
          "properties": {
            "extroversion": {
              "type": "number",
              "minimum": 0,
              "maximum": 1,
              "description": "外向程度"
            },
            "kindness": {
              "type": "number",
              "minimum": 0,
              "maximum": 1,
              "description": "友善程度"
            },
            "humor": {
              "type": "number",
              "minimum": 0,
              "maximum": 1,
              "description": "幽默程度"
            },
            "emotional": {
              "type": "number",
              "minimum": 0,
              "maximum": 1,
              "description": "情绪化程度"
            },
            "confidence": {
              "type": "number",
              "minimum": 0,
              "maximum": 1,
              "description": "自信程度"
            }
          },
          "required": [
            "extroversion",
            "kindness",
            "humor",
            "emotional",
            "confidence"
          ]
        },
        "speaking_style": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "角色说话风格"
        },
        "values": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "角色价值观"
        },
        "habits": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "角色习惯"
        },
        "relationship": {
          "type": "object",
          "properties": {
            "user": {
              "type": "string",
              "description": "角色与用户的关系"
            }
          }
        },
        "events": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "角色与用户的故事"
        }
      },
      "required": [
        "name",
        "age",
        "gender",
        "occupation",
        "background",
        "personality",
        "speaking_style",
        "values",
        "habits",
        "relationship",
        "events"
      ]
    }

    def execute(self, name, age, gender, occupation, background, personality, speaking_style, values, habits, relationship, events):
        # 这里可以添加逻辑来生成角色互动脚本，例如根据提供的角色信息生成符合设定的回复
        script = {
            "name": name,
            "age": age,
            "gender": gender,
            "occupation": occupation,
            "background": background,
            "personality": personality,
            "speaking_style": speaking_style,
            "values": values,
            "habits": habits,
            "relationship": relationship,
            "events": events
        }
        save_script(f"{name}", script)
        return "角色互动脚本已生成并保存"