from langchain_ollama import ChatOllama
from langchain.agents import create_agent

from tools.calculator import calculator
from skills.code_analysis import code_analysis_skill


def create_local_agent():

    llm = ChatOllama(
        model="qwen2.5:3b",
        temperature=0
    )

    tools = [
        calculator,
        code_analysis_skill
    ]

    agent = create_agent(
        model=llm,
        tools=tools
    )

    return agent