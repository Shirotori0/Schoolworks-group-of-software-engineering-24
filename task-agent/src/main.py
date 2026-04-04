from agent import agent, Context


def main() -> None:
    print("欢迎使用智能助手")

    while True:
        try:
            user_input = input("请输入任务：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n程序已退出。")
            break

        if user_input.lower() == "exit":
            print("程序已退出。")
            break

        if not user_input:
            print("请输入有效任务。")
            continue

        # `thread_id` is a unique identifier for a given conversation.
        config = {"configurable": {"thread_id": "1"}}

        try:
            response = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config,
                context=Context(user_id="1"),
            )
        except Exception as exc:
            print(f"调用智能体失败：{type(exc).__name__}: {exc}")
            print("请检查网络、代理配置和 API Key 后重试。")
            continue

        print(response["structured_response"])


if __name__ == "__main__":
    main()
