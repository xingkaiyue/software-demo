# src/main.py
import os
from dotenv import load_dotenv
from utils.xfyun_ws_client import XFYunWSClient
from modules.library_assistant import LibraryAssistant

load_dotenv()  #  必须先加载 .env

#  强烈建议：启动时打印一次，确认不是 None
print("APPID =", os.getenv("XFYUN_APPID"))
print("API_KEY =", os.getenv("XFYUN_API_KEY"))
print("API_SECRET =", os.getenv("XFYUN_API_SECRET"))

client = XFYunWSClient(
    appid=os.getenv("XFYUN_APPID"),
    api_key=os.getenv("XFYUN_API_KEY"),
    api_secret=os.getenv("XFYUN_API_SECRET"),
    url="wss://spark-api.xf-yun.com/v1/x1",
    domain="spark-x"
)

assistant = LibraryAssistant(client)

print("📚 图书馆智能助手已启动（输入 退出 结束）")
while True:
    user = input("读者: ")
    if user in ["退出", "exit", "quit"]:
        print("助手: 感谢您的咨询，欢迎再次使用图书馆服务！")
        break
    print("助手:", assistant.chat(user))