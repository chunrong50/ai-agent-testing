import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

class LLMCLI:

    def run_chat_cli(self):
        print("=== AI Agent 模拟对话终端（输入 q 或 exit 退出） ===")

        # 初始化对话历史，系统提示词固定在第一位
        messages = [
            {"role": "system", "content": "你是一个乐于助人的测试开发助手。"}
        ]

        while True:
            try:
                user_input = input("\n用户: ")
                if user_input.lower() in ["q", "exit"]:
                    print("退出对话。再见！")
                    break

                if not user_input.strip():
                    continue

                # 1. 将用户的输入追加到历史记录中
                messages.append({"role": "user", "content": user_input})

                # 2. 发起多轮对话请求
                response = client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL"),
                    messages=messages,
                    temperature=0.7,
                    max_tokens = 300
                )

                ai_reply = response.choices[0].message.content
                print(f"AI: {ai_reply}")

                # 3. 将 AI 的回复也追加到历史记录中，实现“上下文记忆”
                messages.append({"role": "assistant", "content": ai_reply})

            except Exception as e:
                print(f"发生错误: {e}")
                # 如果出错，把刚才用户输入的那条 pop 掉，防止污染后续对话上下文
                messages.pop()


    def ask_ai_single_turn(self,prompt: str):
        """
        单轮对话函数：接收一个提问，返回大模型的回答
        """
        try:
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL"),  # 替换为你实际使用的模型名称（如 gpt-4o 等）
                messages=[
                    {"role": "system", "content": "你是一个严谨的 AI Agent 测试开发专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 温度调低（0-1），数值越低回答越稳定，适合自动化测试
                max_tokens=500
            )
            # 提取并返回大模型回复的文本
            return response.choices[0].message.content
        except Exception as e:
            return f"API 调用出错: {str(e)}"