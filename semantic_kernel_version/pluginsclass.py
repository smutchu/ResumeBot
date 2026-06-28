
from bs4 import BeautifulSoup
from docx import Document as DocxDocument
import requests
from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments, kernel_function
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion, OllamaChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
import asyncio
from langchain_version.rewrite_langchain import loadresume
from semantic_kernel.agents import ChatCompletionAgent
vector=loadresume("/Users/hravs/Python_projects/ResumeBot/data/Test_Resume_Sample.docx")

class ResumebotPlugin:
 @kernel_function (
            description="gets the score for the jd vs the resume"
    )
 async def get_score(self,jd,kernel:Kernel):
        embed_query=vector.similarity_search(jd,k=10)
        context = "\n\n".join([doc.page_content for doc in embed_query])  
        prompt = "You are a resume fit scorer. Compare this resume {{$context}} to this job description {{$jd}}. Your FIRST line must be exactly 'Score: X/10' where X is a single number. Nothing else on that line. Then on the next line explain what matches and what is missing."
        result = await kernel.invoke_prompt(prompt,arguments=KernelArguments(context=context,jd=jd))
        return result
 @kernel_function(
         description="scrape the jd from the web page"
 )
 def scrape_job_description(self,url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse the HTML
        soup = BeautifulSoup(response.text, "html.parser")
        jd =  soup.find_all("div", class_="article__content")[2].get_text(strip=True)
        return jd

    except Exception as e:
        print(f"Error: {e}")
        return input("please paste the JD, couldn't parse the url: ")
    
 @kernel_function(
         description="ssave the document"
 )
 def save_document(self,response_from_llm):
   doc = DocxDocument() 
   for line in response_from_llm.split("\n"):
      doc.add_paragraph(line)
   doc.save("modified.docx")

 @kernel_function(
     description="modify the resume per jd"
 )
 async def modify_resume(self,jd,kernel:Kernel):
   embed_query=vector.similarity_search(jd,k=10)
   context = "\n\n".join([doc.page_content for doc in embed_query])  
   prompt =  "You are a resume editor. Rewrite the ENTIRE resume below word for word, replacing and tailoring the content to match the job description. Do NOT give advice or suggestions. Do NOT explain what to change. Just output the fully rewritten resume text and nothing else. Here is the resume: {{$context}}. Here is the job description: {{$jd}}."
   response =await kernel.invoke_prompt(prompt,arguments=KernelArguments(context=context,jd=jd))
   return response

        
async def main():    
    kernel = Kernel()
    kernel.add_service(
        OllamaChatCompletion(
            ai_model_id="llama3.2"
        ))
    kernel.add_plugin(ResumebotPlugin(), plugin_name="ResumeBot")
    # score = await kernel.invoke(
    #     plugin_name="ResumeBot",
    #     function_name="get_score",
    #     jd="some test job description")
    # print(score)
    # modify = await kernel.invoke(
    #     plugin_name="ResumeBot",
    #     function_name="modify_resume",
    #     jd="some test job description")
    # print(modify)
    execution_settings = OllamaChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
    agent = ChatCompletionAgent(kernel=kernel,
                                name="ResumeBotAgent",
                                instructions="You are a resume assistant. When given a job description, score the resume against it. Do NOT offer to modify or tailor unless explicitly asked.",
                                function_choice_behavior=FunctionChoiceBehavior.Auto())
    response = await agent.get_response(messages="score my resume against this job: <https://bloomberg.avature.net/careers/JobDetail/Senior-Software-Engineer-Integration/18312?utm_medium=recruitment&utm_content=jobreq&utm_source=linkedIn&source=linkedIn#>")
    print(response)
    

asyncio.run(main())