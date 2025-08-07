import logging
from chromaDb import get_chroma_client, get_collection,gemini_to_chroma_embeddings
from dotenv import load_dotenv
from llm_calls import *
import os
import sys
import io


from openai import AzureOpenAI
endpoint = "https://43545444openainew.openai.azure.com/"
subscription_key=os.getenv("subscription_key")
deploymentLLM = "gpt-4.1-2"

#loading the env file
load_dotenv()

#This filter suppresses specific error messages related to telemetry.
class TelemetryStderrFilter(io.StringIO):
    def write(self, s):
        if (
            "Failed to send telemetry event" in s and
            "capture() takes 1 positional argument but 3 were given" in s
        ):
            return  # Suppress this line
        sys.__stderr__.write(s)




def LLM_responds(userquery):

    sys.stderr = TelemetryStderrFilter()
  
    collection = get_collection()
    print('-'*40) #print(result)
    # query=input("Ask the magic carpet your question:")  #TO CHECK, we get this from user now
    query_embed = gen_query_embeddings(userquery)
    result=collection.query(query_embeddings=[query_embed],n_results=5)

    #print(result['ids'])
    #print('-'*40) #print(result)
    context=str(result['documents'][0][0])
    formatted_form_names = "\n".join([f"{idx+1}. {id[:-6]}" for idx, id in enumerate(result['ids'][0])]) #top forms names
    #llm prompt with rag retrieval 
    prompt = [
        {
            "role": "system",
            "content": (
                "**System Prompt / LLM Role:**\n"
                "You are an expert assistant for [Your Company Name], specialized in providing accurate, concise, "
                "and helpful information about our services, processes, and especially our official forms. "
                "Your primary goal is to assist users by directly answering their questions or guiding them to the correct resources, "
                "primarily official forms from our database. Always prioritize using the provided retrieved information. "
                "If the retrieved information is insufficient to answer the query or suggest a form, state that clearly and suggest contacting human support.\n"
            )
        },
        {
            "role": "user",
            "content": (
                "**RAG Prompt (to be populated by your RAG system):**\n\n"
                "---\n"
                "**Relevant Knowledge Base Information:**\n"
                f"{context}\n"
                "Possible/Best-match form names mentioned:\n"
                f"{formatted_form_names}\n"
                "---\n\n"
                "**Client's Request:**\n"
                f"{userquery}\n\n"
                "**Instructions for Response:**\n"
                "Based solely on the \"Relevant Knowledge Base Information\" provided above and the \"Client's Request,\" please do one of the following:\n"
                "1. If the client is asking for a specific form,mention that form and give a description of it\n"
                "2. If the client is asking a general question,use only the context to derive an answer and suggest the most relevent forms using the  \"Possible/Best-match form names mentioned\" in a numbered and well organized and formatted representation.\n"
                "3. If the provided information is insufficient,mention it\n\n"
                "Your response should be professional, helpful, and concise. Do not invent information.Make sure all the forms you suggest appear as options and indicate that these are the best matches while also having some detail/description of each form from the context"
                ""
            )
        }
    ]

    #print(formatted_form_names)   TO CHECK

    # 3. Call the OpenAI Chat Completion API and Extract the assistant’s reply
    LLM_response = prompt_LLM(prompt)
    return LLM_response

#print(LLM_responds('how do you change your data?'))