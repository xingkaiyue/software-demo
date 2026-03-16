# utils/prompt_loader.py
def load_prompt(name: str) -> str:
    with open(f"src/prompts/{name}", encoding="utf-8") as f:
        return f.read()