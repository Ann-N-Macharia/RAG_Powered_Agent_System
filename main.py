# ===================================================================================
# IMPORT LIBRARIES
# ===================================================================================
import os
from dotenv import load_dotenv
import traceback
from openai import OpenAI, APITimeoutError, RateLimitError, APIError, APIConnectionError
from pathlib import Path
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent #AgentExecutor
from langchain_core.agents import AgentFinish
from langchain_core.prompts import ChatPromptTemplate
from langchain_mcp_adapters.tools import load_mcp_tools
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from modules.data_privacy_engine import privacy_engine


# ===================================================================================
# SET BASE DIRECTORY AND GET THE PATH TO THE DOCUMENTS
# ===================================================================================
BASE_DIR = Path.cwd()

# ===================================================================================
# LOAD ENV VARIABLES AND INITILIAZE OPENAI CLIENT
# ===================================================================================
load_dotenv()

# ===================================================================================
# SET UP PARAMETERS OBJECT TO CONNET TO THE MCP SERVER
# ===================================================================================
server_params = StdioServerParameters(
    command="python",
    args=[ f"{BASE_DIR}/modules/mcp_server.py"]
)

# ===================================================================================
# LLM SET UP
# ===================================================================================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)


# ===================================================================================
# PROMPT SETUP
# ===================================================================================
myprompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful insurance knowledge assistant."
    "Use the query_insurance_knowledge_base tool to answer questions about insurance."
    "Always use the tool - don't guess or make up information."
    "with every response provide an excerpt for to show what you are baing answer off of. I info is not available notify"
    "user thet can reach out directly to the personnel on email 'info@afyashield.co.ke'"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])


async def main():
# try:
    #Create the session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            #tool discovery
            tools_list = await session.list_tools()
            for tool in tools_list.tools:
                print(f"  - {tool.name}: {tool.description}")

            #tool call
            mcp_tools = await load_mcp_tools(session)
            # local_tools = []
            # tools = local_tools+mcp_tools
            print(mcp_tools)

            agent = create_agent(model=llm, tools=mcp_tools)

            while True:

                user_input = input("> ")

                if user_input.lower() == "exit":
                    break

                compliant_object = privacy_engine.mask_phone_number(user_input)

                compliant_input = compliant_object["compliant_payload"]
                type(print(compliant_input))


                response = agent.invoke({
                    "messages": myprompt.format_messages(input = compliant_input)
                })

                print(response["messages"][-1].content)

    # except Exception as e:
        # print(f"Error: {e}")
      
asyncio.run(main())


