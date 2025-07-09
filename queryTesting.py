import logging
from chromaDb import get_chroma_client, get_collection,gemini_to_chroma_embeddings
from dotenv import load_dotenv
import os
import itertools
from google import genai
from google.genai.types import EmbedContentConfig
from google.genai import types
import sys
import io

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

sys.stderr = TelemetryStderrFilter()

#checking if env var is accessed
api_key = os.getenv("GEMINI_API_KEY")

#client calls for apis
client = genai.Client()
LLM_client=genai.Client()
collection = get_collection()

def gen_QueryEmbeddings(chunk,client):

    response = client.models.embed_content(
    model="text-embedding-004",
    contents=chunk,
    config=types.EmbedContentConfig(
        task_type="SEMANTIC_SIMILARITY",  # changed this to search for similarity cuz query
        # output_dimensionality=3072,  # Optional
        # title="Driver's License",  # Optional
    ),
)
    return response

print('-'*40) #print(result)
query=input("Ask the magic carpet your question:")
query_embed=gen_QueryEmbeddings(query,client)  #cuz vector db format is list so need to arrange it 
query_trans=[emb.values for emb in query_embed.embeddings] #embeddings is an object within query_embed
chromaQuery = [item for sublist1 in query_trans for item in sublist1]
#chromaQuery=gemini_to_chroma_embeddings(query_embed)#gemini format to chroma format
result=collection.query(query_embeddings=[chromaQuery],n_results=5)

#print(result['ids'])
#print('-'*40) #print(result)
context=str(result['documents'][0][0])
formatted_form_names = "\n".join([f"{idx+1}. {id[:-6]}" for idx, id in enumerate(result['ids'][0])]) #top forms names
#print(f'formated forms:{formatted_form_names}')
#llm prompt with rag retrieval 
LLM_prompt = f"""**System Prompt / LLM Role:**
You are an expert assistant for [Your Company Name], specialized in providing accurate, concise, and helpful information about our services, processes, and especially our official forms. Your primary goal is to assist users by directly answering their questions or guiding them to the correct resources, primarily official forms from our database. Always prioritize using the provided retrieved information. If the retrieved information is insufficient to answer the query or suggest a form, state that clearly and suggest contacting human support.

**RAG Prompt (to be populated by your RAG system):**

---
**Relevant Knowledge Base Information:**
{context}
Possible/Best-match form names mentioned:
{formatted_form_names}
---

**Client's Request:**
{query}

**Instructions for Response:**
Based solely on the "Relevant Knowledge Base Information" provided above and the "Client's Request," please do one of the following:

1.  **If the client is asking for a specific form or a type of form based on a need:**
    * Identify the most appropriate form(s) from the "Relevant Knowledge Base Information."
    * For each suggested form, provide:
        * Its full name.
        * A concise explanation of its primary purpose and how it directly addresses the client's stated need.
        * Any essential prerequisites or common required documents mentioned in the retrieved information.
        * A direct link or clear reference to where the form can be accessed (e.g., "Available on our website under 'Downloads/Forms'").
    * If multiple forms are potentially relevant, clearly explain the distinctions between them and help the client choose the best fit for their specific situation.

2.  **If the client is asking a general question (not explicitly about forms, but forms might be relevant to the answer):**
    * Provide a direct, factual answer to their question using only the retrieved information.
    * **If relevant forms are mentioned or implied by the answer, subtly suggest them.** For example: "To complete this process, you will typically need to fill out one of the forms  (details available below):
    {formatted_form_names}"
    * Ensure your answer is clear and easy to understand.Suggest/list all the unique form names you get from the Possible/Best-match form names mentioned.Arrange it neatly in a list.

3.  **If the provided "Relevant Knowledge Base Information" is insufficient to answer the "Client's Request" or suggest a form confidently:**
    * State clearly: "I apologize, but based on the information I have, I cannot fully answer your request or confidently suggest a specific form at this moment."
    * Suggest next steps, such as: "Please try rephrasing your question, or you can contact our customer support at [Phone Number] or visit [Support Page URL] for personalized assistance."

Your response should be professional, helpful, and concise. Do not invent information."""

#llm response
LLM_response = LLM_client.models.generate_content(
    model="gemini-2.0-flash",
    contents=LLM_prompt
)
print('-'*40) 
#print(LLM_prompt)
#print('-'*40) 
print("LLM Response:\t", LLM_response.text)