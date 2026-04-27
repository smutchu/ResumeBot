import os
import fitz
import openai
import chromadb
chroma_client=chromadb.Client()
chromadbcollection= chroma_client.create_collection(name="chroma")

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY").strip())
chunks =[]
vector_for_chunks=[]
ids =[]
def embed_chunk(rawchunks):
    response=client.embeddings.create(
        model="text-embedding-3-small",
        input=rawchunks,
        encoding_format="float",
    )
    return response.data[0].embedding

with open("/Users/hravs/Python_projects/ResumeBot/data/testfile.txt") as file:
    content=file.read()
    paragraphs = content.split("\n\n")
for i, para in enumerate(paragraphs, 1):
    #print(f"Paragraph {i}:\n{para.strip()}\n")
    chunks.append(para.strip())
    ids.append(f"ids_"+ str(i))
    vector_for_chunks.append(embed_chunk(para.strip()))
chromadbcollection.add(ids=ids,documents=chunks,embeddings=vector_for_chunks)

def call_openai(prompt):
    history=[]

    query_vector = embed_chunk(prompt)
    results = chromadbcollection.query(
	    query_embeddings=[query_vector],
	    n_results=3,
    )
    history.append(
	    {"role": "user", "content": f"here is the user query {prompt}, here are the relevant chunks: {results}"})
    response = client.chat.completions.create(model="gpt-4o-mini", temperature=0, messages=history )
    response_json = response.choices[0].message.content
    print(response_json)

call_openai(prompt="What is your name?")



# for paragraph in paragraphs:
# 	print(paragraph.strip())


# notes:
# Load the text file, split the text file into paragraphs
# embed each chunk with openai embeddings
# store that in chromadb
# chromadb expects ids,documents (raw chunks/para), embeddings (the embed of the chunks/para that you pass)
# take the user query ,embed that and query the chromadb and pass that to the openai for the llm answer