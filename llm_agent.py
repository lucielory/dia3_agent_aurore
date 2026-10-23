from groq import Groq

from dotenv import load_dotenv
import os


CONTEXT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "context.txt")


class ConversationAgent :
    def __init__(self, conversation_history=None):
        load_dotenv()
        self.groq_client = Groq(api_key=os.environ["GROQ_KEY"])
        self.system_prompt = self.read_file(file_path=CONTEXT_PATH)
        # Mémoire de l'agent : liste de {"role": "user" | "assistant", "content": "..."}
        self.conversation_history = conversation_history if conversation_history is not None else []


    @staticmethod
    def read_file(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()


    def ask_llm(self, question):

        # On envoie le prompt système + tout l'historique + la nouvelle question
        messages = [{"role": "system", "content": self.system_prompt}]
        messages += self.conversation_history
        messages.append({"role": "user", "content": question})

        chat_completion = self.groq_client.chat.completions.create(
            messages=messages,
            model="openai/gpt-oss-120b",
            include_reasoning=False,
        )


        response = chat_completion.choices[0].message.content

        self.conversation_history.append({"role": "user", "content": question})
        self.conversation_history.append({"role": "assistant", "content": response})
        return response


if __name__ == "__main__":
    agent = ConversationAgent()
    while True:
        question = input("Pose ta question (vide pour quitter) :\n")
        if not question:
            break
        response = agent.ask_llm(question)
        print("\n")
        print(response)
        print("\n")
