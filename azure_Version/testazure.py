from langchain_openai import AzureOpenAIEmbeddings

# 1. Your exact values
OPENAI_API_BASE = "https://my-openai-xxx/"
OPENAI_API_KEY = "xxx"
OPENAI_API_VERSION = "2024-02-01" # Required for text-embedding-3 models
DEPLOYMENT_NAME = "embed-test-east"

# 2. Initialize the LangChain Azure Embeddings client
embeddings_model = AzureOpenAIEmbeddings(
    azure_endpoint=OPENAI_API_BASE,
    openai_api_key=OPENAI_API_KEY,
    openai_api_version=OPENAI_API_VERSION,
    azure_deployment=DEPLOYMENT_NAME,
)

try:
    print("Testing LangChain routing...")
    
    # embed_query is LangChain's method for embedding a single string
    vector = embeddings_model.embed_query("hello")
    
    print("\n✅ LANGCHAIN WORKED!")
    print(f"Vector dimensions: {len(vector)}")
    print(f"First 3 numbers: {vector[:3]}")
    
except Exception as e:
    print(f"\n❌ FAILED: {e}")