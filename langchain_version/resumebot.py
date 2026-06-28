
import chromadb
from docx import Document
import openai
import os
import streamlit as st



from openai import OpenAIError
chroma_client = chromadb.Client()
chromadbcollection = chroma_client.get_or_create_collection(name="resume_db")

if "history" not in st.session_state:
    st.session_state.history = []
if "messages" not in st.session_state:
    st.session_state.messages = []
job_compare=""
job_description = ""
job_lines=[]
list_paragraphs=[]
list_vector=[]
id_list=[]
job_embeddings=[]


client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY").strip())

@st.cache_resource
def get_embedding(input):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=input,
        encoding_format="float",
    )
    return response.data[0].embedding

def resumebot(resume):
 try:
    doc = Document(resume)
    for paragraph in doc.paragraphs:
        if paragraph is not None and len(paragraph.text) > 0:
            list_paragraphs.append(paragraph.text)
    for item in range(len(list_paragraphs)):
        i=list_paragraphs[item]
        response = get_embedding(i)
        list_vector.append( response)
        id_list.append(f"Chunk_" + str(item))
    chromadbcollection.add(ids=id_list,
                   documents=list_paragraphs,
                   embeddings=list_vector,)
    print("Resume loaded successfully")

 except OSError as e:
     print(f"OSError occurred while loading the resume, {e}")
     return None
 except Exception as e:
     print(f"Exception occurred while loading the resume, {e}")
     return None

resumebot("/Users/hravs/Python_projects/ResumeBot/data/Test_Resume_Sample.docx")

system_prompt = f"You are a professional resume assistant. Answer questions only based on the context provided."
if len(st.session_state.history) == 0:
    st.session_state.history.append({"role": "system", "content": system_prompt})

def get_completion(prompt):
    try:
        vector=get_embedding(prompt)
        chunks = chromadbcollection.query(query_embeddings=[vector],
                                   n_results=2)
        extracted_chunks = chunks["documents"][0]
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.history.append({"role": "user", "content": f"Here are the relevant parts of the resume: {extracted_chunks}. Now answer this: {prompt}"})
        responsefromai = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=st.session_state.history,
        )
        message = responsefromai.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": message})
        return message
    except OpenAIError as e:
        print(f"Error connecting to OpenAI: {e}")
        st.session_state.history.pop()
        return None


# while True:
#     user_input= input("User: ")
#     if user_input.lower() == "exit":
#         break
#     elif user_input == "":
#         # print("Please enter an input")
#         continue
#     elif user_input.lower() == "help":
#         print(f"""  
#      Available Commands:
#     - help: Show this menu
#     - summary: Get resume summary
#     - skills: List all skills
#     - experience: Show work history  
#     - compare job: Analyze a job posting
#     - clear: Reset conversation
#     - exit: Quit the bot""")
#     elif user_input.lower() == "clear":
#         history.clear()
#         history.append({"role": "system", "content": system_prompt})
#         print("Reset conversation")
#     elif user_input.lower() == "improve":
#         if job_compare:
#             improve_prompt = f"""
#                 Compare the job description against the resume.
#                 - suggest any changes to make the resume ATS friendly
#                 - show before and after example of the changes made
#                 - explain why each changes help in getting the resume picked
#                 - format the resume section ( Experience, skills, etc..)
#                 """

#             responsefromai = get_completion(f" {improve_prompt}")
#             print(f"Bot: {responsefromai}")
#         else:
#             print("Please analyze a job first using 'compare job'")

#     elif user_input.lower() == "compare job":
#         print("paste the job description below.")
#         print("type 'done' when finished.")
#         while True:
#              job_description = input()
#              if job_description.lower() == "":
#                  continue
#              if job_description.lower() == "done":
#                  break
#              else:
#                  job_lines.append(job_description)


#         job_compare='\n'.join(job_lines)

#         if not job_compare:
#             print("no job description provided, please provide a job description'")
#             continue
#         responsefromai = get_completion(f"Analyse the job against the resume. {job_compare}")
#         print(f"Bot: {responsefromai}")
#         job_embeddings=get_embedding(job_compare)
#     elif user_input.lower() == "match score":
#         if not job_compare :
#             print("please provide a job description")
#             continue
#         results= chromadbcollection.query(query_embeddings= [job_embeddings],
#                          n_results=2)
#         responsefromai = get_completion(f"Based on this job description: {job_compare}. Give a match score out of 100 and explain why")
#         print(responsefromai)
#     else:
#         responsefromai = get_completion(user_input)
#         print(f"Bot: {responsefromai}")
for history in st.session_state.messages:
    if history["role"] == "system":continue
    if history["role"]:
        with st.chat_message(history["role"]):
             st.write(history["content"])
user = st.chat_input("hello , your chatbot is here")
if user:
    response=get_completion(user)
    st.rerun()
    #st.write(response)






