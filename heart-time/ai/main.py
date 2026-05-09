from .pipeline.generator import generate_response

# 一个简单的对话流程

print("欢迎来到心语时光！请输入您的问题：")
while True:
    user_input = input("你：")
    if user_input.lower() in ["退出", "exit", "quit"]:
        print("感谢使用心语时光，再见！")
        break
    
    response = generate_response(user_input, user_id="user1") #待完善
    print(f"心语时光：{response}")