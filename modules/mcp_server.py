import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from content_retriever_engine import base_query_engine

# Initialize a named backend server space container
server_app = Server("afyaplus-clinic-server")

@server_app.list_tools()
async def list_tools():
    return [
        Tool(
            name="query_insurance_knowledge_base",
            description="Searches the insurance knowledge base to responds to relevant queries",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's question."
                    }
                },
                "required": ["query"]
            },
        ),  
    ]


@server_app.call_tool()
async def call_tool(name: str, arguments: dict):

    if name == "query_insurance_knowledge_base":
        query = arguments["query"]

        #Validate the input
        if not query:
            return [
                TextContent(
                    type="text",
                    text="Error: Query cannot be empty."
                )
                ]

        #Call the function with error handling
        try:
            response = base_query_engine.query(query)

            return [
                TextContent(
                    type="text",
                    text=str(response)
                )
            ]
        except Exception as e:
              return [
                    TextContent(
                        type="text",
                        text=f"Error querying knowledge base: {str(e)}"
                    )
                ]

async def launch_server():
    # Keep the server running and listening over the standard input/output lines
    async with stdio_server() as (read_stream, write_stream):
        await server_app.run(read_stream, write_stream, server_app.create_initialization_options())



# =========================================================   
#CODE TESTING:
# =========================================================
if __name__ == "__main__":
    asyncio.run(launch_server())