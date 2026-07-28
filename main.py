# ===================================================================================
# IMPORT LIBRARIES
# ===================================================================================
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_mcp_adapters.tools import load_mcp_tools
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import InMemorySaver

# ===================================================================================
# LOAD ENV VARIABLES AND INITILIAZE OPENAI CLIENT
# ===================================================================================
load_dotenv()

# ===================================================================================
# SET BASE DIRECTORY AND GET THE PATH TO THE DOCUMENTS
# ===================================================================================
BASE_DIR = Path.cwd()

# ===================================================================================
# CREATE SERVER PARAMETERS FOR THE MCP SERVER
# ===================================================================================
server_params = StdioServerParameters(
    command="python",
    args=[f"{BASE_DIR}/modules/mcp_server.py"]
)

# ===================================================================================
# LLM SET UP
# ===================================================================================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

# ===================================================================================
# SYSTEM PROMT SETUP
# ===================================================================================
# SYSTEM_PROMPT = """
# You are a helpful insurance knowledge assistant.
# Use the query_insurance_knowledge_base tool to answer questions about insurance.
# Always use the tool - don't guess or make up information. with every response provide an
# excerpt to show what you are basing answer off of. If info is not available notify"
# user they can reach out directly to the personnel on email 'info@afyashield.co.ke'
# """

SYSTEM_PROMPT = (
    BASE_DIR/"system_prompt.txt"
).read_text(encoding="utf-8")


# ===================================================================================
# LOCAL TOOLS SETUP
# ===================================================================================
@tool
def calculate_medication_dosage(patient_weight_kg: float, dosage_mg_per_kg: float) -> str:
    """
    This function safely calculates the total medication dosage required based on patient weight
    and a specific dosage rate (e.g., 15mg/kg for malaria treatment).

    Args:
        patient_weight_kg (float): The patient's body weight in kilograms.
        dosage_mg_per_kg (float): The prescribed dosage rate in mg per kg of body weight.

    Returns:
        str: A formatted string stating the total calculated dosage in mg, or a
             validated error message if inputs are unsafe or invalid.
    """
    try:
        # Defensive validation: Ensure inputs are logical for a medical context
        if patient_weight_kg <= 0:
            return "Error: Patient weight must be a positive numerical value."

        if dosage_mg_per_kg <= 0:
            return "Error: Dosage rate must be a positive numerical value."

        # Perform the calculation
        total_dosage_mg = patient_weight_kg * dosage_mg_per_kg

        return f"Based on a weight of {patient_weight_kg}kg and a rate of {dosage_mg_per_kg}mg/kg, the total dosage is {total_dosage_mg:.2f} mg."

    except TypeError:
        # Handle cases where non-numeric data might bypass initial filters
        return "Error: Invalid input types. Please provide weight and dosage as numbers."
    except Exception as e:
        # Catch-all for unexpected computational errors to prevent system crashes
        return f"A safety error occurred during calculation: {str(e)}"


# ===================================================================================
# CONNECTION TO MCP SERVER TO ACCESS TOOLS
# ===================================================================================
async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Load tools
            local_tool = [calculate_medication_dosage]
            mcp_tools = await load_mcp_tools(session)
            print(mcp_tools)
            tools = local_tool+ mcp_tools
            print(f"Loaded {len(tools)} tools: {[tool.name for tool in tools]}")

            # Create agent with a checkpointer so it remembers prior turns
            checkpointer = InMemorySaver()
            agent = create_agent(
                model=llm,
                tools=tools,
                system_prompt=SYSTEM_PROMPT,
                checkpointer=checkpointer
            )

            # thread_id ties every turn in this run to the same conversation state
            config = {"configurable": {"thread_id": "cli-session-1"}}

            print("\nAgent ready! Ask about insurance (type 'exit' to quit)\n")

            while True:
                user_input = input("You: ")

                if user_input.lower() == "exit":
                    break

                # Invoke agent - checkpointer + config makes this stateful across turns
                response = await agent.ainvoke(
                    {"messages": [("human", user_input)]},
                    config=config
                )


                # Extract the response
                if "messages" in response:
                    print(f"Agent: {response['messages'][-1].content}\n")
                else:
                    print(f"Agent: {response}\n")

if __name__ == "__main__":
    asyncio.run(main())

# ===================================================================================
# NOTES
# ===================================================================================
# What changed vs. client_test.py:
#   1. Added `from langgraph.checkpoint.memory import InMemorySaver`.
#   2. Removed the second `agent = create_agent(model=llm, tools=mcp_tools)` call,
#      which was silently overwriting the first agent (dropping the local tool and
#      SYSTEM_PROMPT) before the loop ever ran.
#   3. Passed `checkpointer=checkpointer` into create_agent, and defined a fixed
#      `config = {"configurable": {"thread_id": "cli-session-1"}}`.
#   4. Passed that same `config` into every `agent.ainvoke(...)` call in the loop.
#
# How this makes the conversation stateful:
#   create_agent builds a LangGraph graph under the hood. Without a checkpointer,
#   each `ainvoke` call runs the graph fresh - it only knows about the single
#   human message you just sent, with no memory of earlier turns.
#
#   Attaching `checkpointer=InMemorySaver()` tells the graph to persist its state
#   (the full running message list) after every invocation, keyed by `thread_id`.
#   Because every call in the while loop reuses the same `thread_id`
#   ("cli-session-1"), LangGraph looks up that thread's saved state before running,
#   prepends the prior conversation history to the new input automatically, and
#   saves the updated history back afterward. That's why you never have to
#   manually build up a messages list yourself - the checkpointer + thread_id
#   combination is what threads memory through each turn of the while loop.
#
#   Caveat: InMemorySaver only lives in process memory, so history resets each
#   time the script restarts. For persistence across runs, swap it for
#   SqliteSaver or PostgresSaver (same checkpointer= interface).
