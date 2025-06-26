from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from dotenv import load_dotenv
import os
from langchain_community.utilities import SerpAPIWrapper

# Load .env variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment!")
print("GROQ_API_KEY loaded successfully.")

serpapi_api_key = os.getenv("SERPAPI_API_KEY")
if not serpapi_api_key:
    raise ValueError("SERPAPI_API_KEY not found in environment!")
print("SERPAPI_API_KEY loaded successfully.")

web_search = SerpAPIWrapper(serpapi_api_key=serpapi_api_key)

app = FastAPI()

# Setup Groq LLM
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")

# Define routing output model
class RoutingOutput(BaseModel):
    datasource: Literal["ai_response", "vectorstore", "wiki_search", "web_search"]


# Setup routing logic
def get_router_chain():
    system_prompt = (
        "You are a router. Send sound or document-based questions to 'vectorstore', "
        "greetings or personal messages to 'ai_response', "
        "factual questions to 'wiki_search', "
        "and current event or real-time queries to 'web_search'."
    )

    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{question}")])
    return prompt | llm.with_structured_output(RoutingOutput)

# Wikipedia fallback
wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=400))

# Request schema
class QueryRequest(BaseModel):
    query: str
    context: str

# Basic LLM completion endpoint
@app.post("/AI_Answer/")
def ai_answer(req: QueryRequest):
    try:
        response = llm.invoke(f"Context:\n{req.context}\n\nQ: {req.query}\nA:")
        return {"message": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def split_query_if_needed(query: str):
    import re
    return [q.strip() for q in re.split(r"\band\b|\&|\n", query, flags=re.IGNORECASE) if q.strip()]

# Smart router endpoint
# @app.post("/Smart_AI_Answer/")
# def smart_ai_answer(req: QueryRequest):
#     # try:
#     router_chain = get_router_chain()
    #     routed = router_chain.invoke({"question": req.query})
    #     route = routed.datasource

    #     print(f"Routing decision: {route}")

    #     if route == "ai_response":
    #         answer = llm.invoke(req.query).content
    #         return {"path": "AI Response", "message": answer}

    #     elif route == "vectorstore":
    #         prompt = f"Context:\n{req.context}\n\nQ: {req.query}\nA:"
    #         answer = llm.invoke(prompt).content
    #         return {"path": "Vectorstore", "message": answer}

    #     elif route == "wiki_search":
    #         return {"path": "Wikipedia Search", "message": wiki.run(req.query)}
        
    #     elif route == "web_search":
    #         return {"path": "Web Search", "message": web_search.run(req.query)}


    #     else:
    #         raise ValueError("Invalid route decision")

    # except Exception as e:
    #     import traceback
    #     traceback.print_exc()
    #     raise HTTPException(status_code=500, detail=str(e))
@app.post("/Smart_AI_Answer/")
def smart_ai_answer(req: QueryRequest):
    try:
        router_chain = get_router_chain()
        # routed = router_chain.invoke({"question": req.query})
        queries = split_query_if_needed(req.query)
        responses = []

        for q in queries:
            routed = router_chain.invoke({"question": q})
            route = routed.datasource
            print(f"Routing '{q}' to {route}")

            if route == "ai_response":
                message = llm.invoke(q).content

            elif route == "vectorstore":
                message = llm.invoke(f"Context:\n{req.context}\n\nQ: {q}\nA:").content

            elif route == "wiki_search":
                message = wiki.run(q)

            elif route == "web_search":
                message = web_search.run(q)

            else:
                message = "Unknown route."

            responses.append({"path": route, "message": message})

        return {
            "message": "\n\n".join(f"{r['path']}: {r['message']}" for r in responses)
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
