from utils.prompt_loader import load_prompt
from utils.knowledge_loader import load_knowledge
from modules.dialog_manager import DialogManager

class LibraryAssistant:
    def __init__(self, ws_client):
        self.client = ws_client

        system_prompt = load_prompt("library_system.txt")
        knowledge = load_knowledge("library_rules.txt")

        # ⭐ 核心：规则 + 知识 合并
        full_prompt = f"""
{system_prompt}

【以下是图书馆真实规则，必须严格遵守】
{knowledge}

回答要求：
- 只能基于以上规则回答
- 如果规则中没有明确说明，请回答“该问题需人工确认”
"""

        self.dialog = DialogManager(full_prompt)

    def chat(self, user_input: str) -> str:
        messages = self.dialog.build_messages(user_input)
        reply = self.client.chat(messages)
        self.dialog.append_assistant(reply)
        return reply