# ===================================================================================
# IMPORT LIBRARIES
# ===================================================================================
from modules.data_privacy_engine import privacy_engine

# # 1.masking
# message = "My name is Annie, my phone number is +254dfghjklkjhg"
# output_dict = privacy_engine.mask_phone_number(message)
# print(output_dict)

# message_status = output_dict["status"]
# compliant_payload = output_dict["compliant_payload"]
# pii_vault = output_dict["secure_vault"]

# print(message_status)
# print(compliant_payload)
# print(pii_vault)

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pathlib import Path

# ===================================================================================
# SET BASE DIRECTORY AND GET THE PATH TO THE DOCUMENTS
# ===================================================================================
BASE_DIR = Path.cwd()

# ===================================================================================
# SET UP PARAMETERS OBJECT TO CONNET TO THE MCP SERVER
# ===================================================================================
server_params = StdioServerParameters(
    command="python",
    args=[ f"{BASE_DIR}/modules/mcp_server.py"]
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Discovered tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

asyncio.run(main())