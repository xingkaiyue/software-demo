def load_knowledge(name: str) -> str:
    with open(f"src/knowledge/{name}", encoding="utf-8") as f:
        return f.read()