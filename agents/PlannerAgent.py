import logging
from openai import OpenAI  # type: ignore
from utils.schemas import Plan

logger = logging.getLogger(__name__)


class PlannerAgent:
    def __init__(
        self,
        dev_prompt,
        llm,
        messages,
        tools,
        model_name: str = "gpt-4.1-mini",
    ):
        self.model_name = model_name
        self.dev_prompt = dev_prompt
        self.llm: OpenAI = llm
        self.messages = messages
        self.tools = tools
        if self.dev_prompt:
            self.messages.append({"role": "developer", "content": self.dev_prompt})

    def add_messages(self, query: str):
        """Add a message to the messages list.

        Args:
            query (str): The message to add.

        Returns:
            None
        """
        self.messages.append({"role": "user", "content": query})

    def plan(self, query: str):
        """Create a detailed plan to complete the request of the user.

        Args:
            query (str): The request of the user.

        Returns:
            Plan: The plan to complete the request of the user.
        """
        self.add_messages(query=query)
        response = self.llm.responses.parse(
            model=self.model_name,
            input=self.messages,
            tools=self.tools,
            text_format=Plan,
        )
        return response
