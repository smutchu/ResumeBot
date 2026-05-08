from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
import os
from dotenv import load_dotenv
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader
import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
openai_key = os.getenv("AZURE_OPENAI_KEY")
openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
openai_embed_deployment = os.getenv("AZURE_EMBED_DEPLOYMENT")
search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_SEARCH_KEY")
api_version = os.getenv("OPENAI_API_VERSION")
embed_api_version = os.getenv("AZURE_EMBED_API_VERSION")
index = os.getenv("AZURE_SEARCH_INDEX")

# Chat LLM
llm = AzureChatOpenAI(
    api_version=api_version,
    azure_deployment=openai_deployment,
    azure_endpoint=openai_endpoint,
    api_key=openai_key
)

# Embeddings
# NOTE: Azure AI Foundry compatibility issue with LangChain SDK.
# TODO: Fix embeddings when Azure resolves Foundry/classic SDK sync issue.
embeddings = AzureOpenAIEmbeddings(
    azure_deployment=openai_embed_deployment,
    azure_endpoint=openai_endpoint,
    api_key=openai_key,
    openai_api_version=embed_api_version,
)

# Vector store
vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=search_endpoint,
    azure_search_key=search_key,
    index_name=index,
    embedding_function=embeddings.embed_query,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

@st.cache_resource
def loadresume(resume):
    try:
        loader = Docx2txtLoader(resume)
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = text_splitter.split_documents(data)
        print(f"Number of chunks: {len(chunks)}")
        vector_store.add_documents(documents=chunks)
        return vector_store
    except OSError as e:
        print(f"OSError occurred while loading the resume: {e}")
        return None
    except Exception as e:
        print(f"Exception occurred while loading the resume: {e}")
        return None


def InvokeAzure(prompt, vector_store):
    results = vector_store.similarity_search(prompt, k=2)
    context = "\n\n".join([doc.page_content for doc in results])

    template = ChatPromptTemplate.from_messages([
        ("system", "You are a resume assistant. Answer only based on this resume context {context}"),
        ("human", "{question}")
    ])

    parser = StrOutputParser()
    chain = template | llm | parser
    return chain.invoke({"context": context, "question": prompt})


vs = loadresume("/Users/hravs/Python_projects/ResumeBot/data/Test_Resume_Sample.docx")

for history in st.session_state.messages:
    if history["role"] == "system":
        continue
    with st.chat_message(history["role"]):
        st.write(history["content"])

user = st.chat_input("Hello, your chatbot is here")
if user:
    result = InvokeAzure(user, vs)
    st.session_state.messages.append({"role": "user", "content": user})
    st.session_state.messages.append({"role": "assistant", "content": result})
    st.rerun()