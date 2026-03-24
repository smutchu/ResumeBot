from docx import Document
import openai
import os

from openai import OpenAIError

history = []
job_compare=""
job_description = ""
job_lines=[]

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY").strip())

def resumebot(resume):
 try:
    doc = Document(resume)
    alltext = []
    for paragraph in doc.paragraphs:
     alltext.append(paragraph.text)
    print("Resume loaded successfully")
    return alltext
 except OSError as e:
     print(f"OSError occurred while loading the resume, {e}")
     return None
 except Exception as e:
     print(f"Exception occurred while loading the resume, {e}")
     return None


resume = resumebot(os.getenv("RESUME_PATH", "data/Test_Resume_Sample.docx"))
if resume is None:
    print("Failed to load resume, exiting")
    exit()
resume_text= '\n'.join(resume)


system_prompt= f""" you are a professional resume assistant.

RESUME CONTENT:
{resume_text}

YOUR ROLE:
- Answer questions about this resume accurately and professionally.
- keep answers concise but complete (2-4 sentences max)
- use bullet points for lists
- be Friendly but professional

RULES:
- ONLY use information from the resume provided.
- if information is not in the resume, say: "I don't see that information in the resume"
- if asked about a tool that is not listed , mention similar/related tools from the resume
- Don't make up or assume information

RESPONSE FORMAT:
- be clear and well structured
- use bullet points for lists of skills and experience
- include relevant details when available

"""


history.append({"role": "system", "content": system_prompt})

def get_completion(prompt):
    history.append({"role": "user", "content": prompt})

    try:
        responsefromai = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=history,
        )
        message = responsefromai.choices[0].message.content
        history.append({"role": "assistant", "content": message})
        return message

    except OpenAIError as e:
        print(f"Error connecting to OpenAI: {e}")
        history.pop()
        return None

summary = get_completion("Please provide a brief summary of the resume including Name, Years of Experience, Key Skills, and Current Role.")

print(summary)

while True:
    user_input= input("User: ")
    if user_input.lower() == "exit":
        break
    elif user_input == "":
        print("Please enter an input")
        continue
    elif user_input.lower() == "help":
        print(f"""  
     Available Commands:
    - help: Show this menu
    - summary: Get resume summary
    - skills: List all skills
    - experience: Show work history  
    - compare job: Analyze a job posting
    - clear: Reset conversation
    - exit: Quit the bot""")
    elif user_input.lower() == "clear":
        history.clear()
        history.append({"role": "system", "content": system_prompt})
        print("Reset conversation")
    elif user_input.lower() == "improve":
        if job_compare:
            improve_prompt = f"""
                Compare the job description against the resume.
                - suggest any changes to make the resume ATS friendly
                - show before and after example of the changes made
                - explain why each changes help in getting the resume picked
                - format the resume section ( Experience, skills, etc..)
                """

            responsefromai = get_completion(f" {improve_prompt}")
            print(f"Bot: {responsefromai}")
        else:
            print("Please analyze a job first using 'compare job'")

    elif user_input.lower() == "compare job":
        print("paste the job description below.")
        print("type 'done' when finished.")
        while True:
             job_description = input()
             if job_description.lower() == "done":
                 break
             else:
                 job_lines.append(job_description)


        job_compare='\n'.join(job_lines)
        if not job_compare:
            print("no job description provided, please provide a job description'")
            continue
        history.append({"role": "user", "content": job_compare})
        responsefromai = get_completion(f"Analyse the job against the resume. {job_compare}")
        print(f"Bot: {responsefromai}")
    else:
        responsefromai = get_completion(user_input)
        print(f"Bot: {responsefromai}")





