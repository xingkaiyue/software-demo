# modules/dialog_manager.py
class DialogManager:
    def __init__(self, system_prompt):
        self.messages = [
            {"role": "system", "content": system_prompt}
        ]

    def build_messages(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        return self.messages

    def append_assistant(self, reply):
        self.messages.append({"role": "assistant", "content": reply})