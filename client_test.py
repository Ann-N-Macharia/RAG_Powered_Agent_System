# minimal_mcp_agent.py
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_mcp_adapters.tools import load_mcp_tools
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# Setup
BASE_DIR = Path.cwd()
server_params = StdioServerParameters(
    command="python",
    args=[f"{BASE_DIR}/modules/mcp_server.py"]
)

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

# System instructions
SYSTEM_PROMPT = """You are a helpful insurance knowledge assistant. 
Use the query_insurance_knowledge_base tool to answer questions about insurance.
Always use the tool - don't guess or make up information. with every response provide an 
excerpt to show what you are basing answer off of. If info is not available notify"
user they can reach out directly to the personnel on email 'info@afyashield.co.ke'"""


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Load tools
            local_tool = []
            mcp_tools = await load_mcp_tools(session)
            tools = local_tool+mcp_tools
            print(f"📦 Loaded {len(tools)} tools: {[tool.name for tool in tools]}")
            
            # Create agent
            agent = create_agent(
                model=llm,
                tools=tools,
                system_prompt=SYSTEM_PROMPT
            )

            agent = create_agent(model=llm, tools=mcp_tools)
            
            print("\n🤖 Agent ready! Ask about insurance (type 'exit' to quit)\n")
            
            while True:
                user_input = input("💭 You: ")
                if user_input.lower() == "exit":
                    break
                
                # Invoke agent - KEY FIX: Use the right message format
                response = await agent.ainvoke({
                    "messages": [("human", user_input)]
                })

              
                # Extract the response
                if "messages" in response:
                    print(f"🤖 Agent: {response['messages'][-1].content}\n")
                else:
                    print(f"🤖 Agent: {response}\n")

if __name__ == "__main__":
    asyncio.run(main())