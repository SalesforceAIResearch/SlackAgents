from agent.assistant import assistant


if __name__ == "__main__":
    message = "Can you help me search some videos about Fei-Fei Li's recent research on AI?"
    response = assistant.chat(message)
    print(response)