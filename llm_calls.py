from dotenv import load_dotenv
import os
load_dotenv()

endpoint = "https://43545444openainew.openai.azure.com/"
subscription_key=os.getenv("subscription_key")
deploymentLLM = "gpt-4.1-2"

client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint="https://43545444openainew.openai.azure.com/",
    api_key=subscription_key,
    ) 
    

def gen_embeddings(chunk):
    """Generate embeddings for documents"""
    response = client.embeddings.create(
        input=chunk,
        model="text-embedding-3-small"
    )
    #print(response)
    embeddings=[item.embedding for item in response.data]
    print(f'len of emebedding vector:{len(embeddings)}')
    return embeddings
    # return response.data[0].embedding


def gen_query_embeddings(chunk):
    """Generate embeddings for queries"""
    response = client.embeddings.create(
        input=chunk,
        model="text-embedding-3-small"
    )
    embeddings=[item.embedding for item in response.data]
    print(f'len of query vector:{len(embeddings)}')
    return response.data[0].embedding

def prompt_LLM(prompt):
   
    response = client.chat.completions.create(
    messages=prompt,
    max_completion_tokens=800,
    temperature=1.0,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    model="gpt-4.1-2",
)
    return response.choices[0].message.content