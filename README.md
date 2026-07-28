# AfyaPlus Health Enterprise Agent

A RAG-powered conversational agent for medical insurance verification and clinical routing. It grounds its answers in a local insurance knowledge base, exposes that knowledge base as a tool over the Model Context Protocol (MCP), and masks personally identifiable information (PII) before any text reaches the LLM.

## How it works

```
User input
   │
   ▼
DataPrivacyEngine.mask_pii   (Kenyan phone numbers / emails → [masked_phone]_N, [masked_email]_N)
   │
   ▼
LangChain agent (create_agent)  ──uses──▶  calculate_medication_dosage (local tool)
   │                                  └──▶  query_insurance_knowledge_base (MCP tool, stdio)
   │                                              │
   │                                              ▼
   │                                   LlamaIndex VectorStoreIndex
   │                                   over documents/Insurance_policies.txt
   ▼
DataPrivacyEngine.demask_pii  (restores original PII in the response)
   │
   ▼
Response printed to user
```

- **Retrieval**: [modules/content_retriever_engine.py](modules/content_retriever_engine.py) loads files from `documents/`, splits them with LlamaIndex's `SentenceSplitter`, and builds a `VectorStoreIndex` queried via `base_query_engine`.
- **MCP server**: [modules/mcp_server.py](modules/mcp_server.py) wraps that query engine as an MCP tool, `query_insurance_knowledge_base`, served over stdio.
- **Agent**: [main.py](main.py) is the entry point. It spawns the MCP server as a subprocess, loads its tools via `langchain-mcp-adapters`, adds a local `calculate_medication_dosage` tool, and builds a LangChain agent (`create_agent`) using the system prompt in [system_prompt.txt](system_prompt.txt).
- **Statefulness**: the agent is built with a LangGraph `InMemorySaver` checkpointer and a fixed `thread_id`, so conversation history persists automatically across turns of the `while` loop for the life of the process.
- **PII protection**: [modules/data_privacy_engine.py](modules/data_privacy_engine.py) regex-matches Kenyan phone numbers and emails, replaces them with placeholder tokens before the LLM sees them, and restores the originals in the final response — per the compliance guardrails defined in `system_prompt.txt`.

## Project structure

```
.
├── main.py                          # Main entry point (stateful agent + PII masking)
├── client_test.py                   # Earlier client variant (no checkpointer)
├── client_test_stateful.py          # Client variant with checkpointer added
├── system_prompt.txt                # Agent role, boundaries, and output requirements
├── requirements.txt
├── documents/
│   └── Insurance_policies.txt       # Source knowledge base
└── modules/
    ├── mcp_server.py                # MCP server exposing the RAG tool over stdio
    ├── content_retriever_engine.py  # LlamaIndex ingestion + vector index/query engine
    └── data_privacy_engine.py       # PII masking / demasking
```

## Setup

1. Create and activate a virtual environment, then install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the project root with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-key-here
   ```

## Running

Run the main entry point from the project root (it launches the MCP server automatically as a subprocess):

```bash
python main.py
```

Type a question at the `You:` prompt (e.g. *"Is AfyaShield Partner Pharmacy Limuru an approved pharmacy?"*) or type `exit` to quit.

## Known limitations

- `InMemorySaver` only persists conversation state for the current process — history resets on restart. Swap it for `SqliteSaver`/`PostgresSaver` (same `checkpointer=` interface) for cross-run persistence.
- PII masking currently covers Kenyan phone numbers and email addresses only.
