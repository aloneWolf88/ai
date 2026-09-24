class ContextManager:

    def __init__(self):
        self.items = []

    def add(self, name, content):
        self.items.append({
            "name": name,
            "content": content
        })

    def build(self):
        if not self.items:
            return ""

        context = []

        for item in self.items:
            context.append(
                f"[{item['name']}]\n"
                f"{item['content']}"
            )

        return "\n\n".join(context)

    def clear(self):
        self.items.clear()