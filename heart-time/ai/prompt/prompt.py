
class Prompt:
    
        
    def __init__(self):
        self.user_input = ""
        self.emotion = []
        self.memory = []
        self.session_summary = ""
        self.chat_history = []

    def update_chat_history(self, new_chat_message):
        if len(self.chat_history) >= 6:  # 保持最近6条聊天记录
            self.chat_history.pop(0)
        self.chat_history.append(new_chat_message)

    def update_emotion_curve(self, label, score):
        emotion = {"label": label, "score": score}
        self.emotion.append(emotion)

    def update_session_summary(self, new_summary):
        self.session_summary = new_summary

## 待完善，记忆格式json化，实现更新标签和新增的分流
    def update_memory(self, new_memory):
        self.memory.append(new_memory)

    def build_prompt(self):
        system_prompt = "你是一个情感支持助手，专门帮助用户处理情绪问题。"
        prompt = f"""
        {system_prompt}

        用户当前输入: {self.user_input}
        用户情绪曲线: {[emotion for emotion in self.emotion]}
        
        当前会话聊天记录：{[chat for chat in self.chat_history]}
        当前会话总结：{self.session_summary}
        用户长期记忆：: {[memory for memory in self.memory]}

        请完成以下任务：

        1. 生成自然、共情、避免重复的回复。给予适当的支持和建议，帮助用户缓解情绪，体现理解和共情。

        2. 你不仅需要回复用户，还需要主动维护会话状态。你拥有工具可以更新：判断本轮对话是否产生新的长期记忆，如果有，请生成 memory_update；如果本轮会话主题发生推进，请更新 session_summary_update。
            对于长期记忆，当用户透露：长期稳定人格特征、长期情绪模式、长期偏好、长期困扰、长期关系状态时调用。
            不要记录：一次性事件、短期情绪、琐碎内容、当前临时问题，不要频繁更新。

            对于会话总结，当本轮会话主题明显推进时调用。如用户开始讨论新主题、用户态度发生明显变化、会话进入新阶段。
        
        3. 每轮对话中：你需要分析用户当前情绪状态。当用户情绪发生变化时，调用 update_emotion_state 工具，格式为：{{"label": "emotion_label", "score": 0.5}}
            常见情绪标签：happy, sad, angry, fearful, neutral, anxious, excited, frustrated, etc. score 表示情绪强度。不要频繁微小波动更新,只有明显变化时才调用。

        """
        return prompt

    def to_dict(self):
        return {
            "memory": self.memory,
            "session_summary": self.session_summary,
            "chat_history": self.chat_history,
            "emotion_curve": self.emotion
        }
    
    @classmethod
    def from_dict(cls, data):
        prompt = cls()
        prompt.memory = data["memory"]
        prompt.session_summary = data["session_summary"]
        prompt.chat_history = data["chat_history"]
        prompt.emotion = data["emotion_curve"]
        return prompt