class Memory:

    def __init__(self, max_messages=10):
        self.max_messages = max_messages
        self.messages = []

    def add(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })

        # 너무 많은 대화가 쌓이지 않도록 제한
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_messages(self):
        return self.messages

    def build(self):
        if not self.messages:
            return ""

        result = []

        for message in self.messages:
            role = message["role"]
            content = message["content"]

            if role == "user":
                result.append(f"사용자: {content}")

            elif role == "assistant":
                result.append(f"AI: {content}")

        return "\n".join(result)

    def clear(self):
        self.messages.clear()