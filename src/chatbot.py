from abc import ABC

from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory

from logger import LOG

# 用于存储历史聊天
store = {}


class ChatBot(ABC):
    def __init__(self, prompt_file, session_id=None):
        self.chatbot = None
        self.chatbot_with_history = None
        self.prompt_file = prompt_file
        self.session_id = session_id if session_id else "demo_chatppt_session"
        self.system_prompt = self.load_system_prompt()
        self.create_chatbot()

    def load_system_prompt(self):
        try:
            with open(self.prompt_file, "r", encoding="utf-8") as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到提示文件 {self.prompt_file}!")

    @staticmethod
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            # 如果 store 中没有 session_id 的记录, 创建一个新的内存聊天历史实例
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    def create_chatbot(self):
        system_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),  # 系统提示词
            MessagesPlaceholder(variable_name="messages")  # 消息占位符
        ])

        # 初始化 ChatOllama 模型, 配置参数
        self.chatbot = system_prompt | ChatOllama(model="llama3.1:8b-instruct-q8_0")

        # 将聊天机器人与消息历史记录关联
        self.chatbot_with_history = RunnableWithMessageHistory(self.chatbot, self.get_session_history)

    def chat_with_history(self, user_input, session_id=None):
        if session_id is None:
            session_id = self.session_id

        response = self.chatbot_with_history.invoke(
            [HumanMessage(content=user_input)], # 将用户输入封装为 HumanMessage
            {"configurable": {"session_id": session_id}}
        )

        LOG.debug(f"[ChatBot] {response.content}")
        return response.content