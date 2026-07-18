# ===================================================================================
# IMPORT LIBRARIES
# ===================================================================================
import os
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from pathlib import Path
from dotenv import load_dotenv


# ===================================================================================
# LOAD ENVIRONMENT VARIABLES
# ===================================================================================
load_dotenv()


# ===================================================================================
# ENV VARIABLES ERROR HANDLING
# ===================================================================================
if not os.environ.get("OPENAI_API_KEY"):
   raise ValueError("CRITICAL: OPENAI_API_KEY is unassigned.")


# ===================================================================================
# SET BASE DIRECTORY AND GET THE PATH TO THE DOCUMENTS
# ===================================================================================
BASE_DIR = Path.cwd()
document_path = f"{BASE_DIR}/documents"


# ===================================================================================
# LOAD DOCUMENTS VIA LLAMA INDEX
# ===================================================================================
reader = SimpleDirectoryReader(document_path)
documents = reader.load_data()


# ===================================================================================
# DOCUMENT CHUNKING USING SENTENSE SPLITTER
# ===================================================================================
parser = SentenceSplitter(chunk_size=256, chunk_overlap=30)
nodes = parser.get_nodes_from_documents(documents)
print(f"Successfully generated {len(nodes)} structural document nodes.")


# ===================================================================================
# BUILDING VECTOR INDEX
# ===================================================================================
print("--- Compiling VectorStore Index & Query Engine ---")
index = VectorStoreIndex(nodes)

# ===================================================================================
# CREATING QUERY ENGINE FROM VECTOR INDEX
# ===================================================================================
base_query_engine = index.as_query_engine(similarity_top_k=3)


# =========================================================   
#CODE TESTING:
# =========================================================
if __name__ == "__main__":
#    query = "What is the waiting period policy"
   query = "What is the waiting period policy for maternity and specialised treatment"
   print(f"\nExecuting Index Query: {query}")
   response = base_query_engine.query(query)
   print(response.response)
