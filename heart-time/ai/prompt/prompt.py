
def build_prompt(user_input, emotion, memory):
    system_prompt = "你是一个情感支持助手，专门帮助用户处理情绪问题。"
    prompt = f"""
    {system_prompt}

    用户输入: {user_input}
    用户当前情绪: {emotion['label']} (score: {emotion['score']})
    用户故事、相关历史: {memory}
    
    基于用户输入，当前情绪、记忆，请生成一个合适的回复，
    做到：
    1. 回复要体现对用户情绪的理解和共情。
    2. 避免重复，避免产生重复的回复。
    3.给予适当的支持和建议，帮助用户缓解情绪。
    """
    return prompt
    