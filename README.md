ResumeBot
I built this to learn RAG. You load a resume and chat with it — ask about skills, experience, whatever.
It chunks the resume, stores it in ChromaDB, and when you ask something it finds the relevant parts and passes them to a local LLM to answer.
Stack

LangChain, ChromaDB, HuggingFace Embeddings, Ollama (llama3.2), Streamlit

Run it
bashpip install langchain langchain-chroma langchain-huggingface langchain-ollama streamlit python-docx

# install ollama from ollama.com then:
ollama pull llama3.2

streamlit run resumebot.py
