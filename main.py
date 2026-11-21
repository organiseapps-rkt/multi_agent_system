import os
from typing import TypedDict, Annotated
import operator

import psycopg
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import(
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

from langchain_groq import ChatGroq

from tools.tavily_tools import tavily_search
from tools.flight_tools import search_flights
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
)  

DATABASE_URL = os.getenv("DATABASE_URL")

# for langgraph always create state(shared memory) before creating graph

class TravelState(TypedDict):
    message: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int


def flight_agent(state: TravelState):
    user_query = state["user_query"]
    flight_results = search_flights(user_query)
    state["flight_results"] = flight_results
    state['message'].append(AIMessage(content=f"Flight results fetched")) 
    state["llm_calls"] = state.get("llm_calls", 0) + 1
    return state

def hotel_agent(state: TravelState):
    user_query = f"Best hotels for {state['user_query']}"
    hotel_results = tavily_search(user_query)
    state["hotel_results"] = hotel_results
    state['message'].append(AIMessage(content=f"Hotel information fetched")) 
    state["llm_calls"] = state.get("llm_calls", 0) + 1
    return state

def itinerary_agent(state: TravelState):
    user_query = state["user_query"]
    flight_results = state.get("flight_results", "")
    hotel_results = state.get("hotel_results", "")
    
    prompt = f"""
    Create a travel itinerary for the following.
    user query: 
    {user_query}. 

    Include flight details: 
    {flight_results} 

    and hotel details: 
    {hotel_results}.
    """

    response = llm.invoke(
        input=[
            SystemMessage(content="You are a expert travel assistant"),
            HumanMessage(content=prompt)
        ]
    )

    state["itinerary"] = response.content
    state['message'].append(AIMessage(content=f"Itinerary generated")) 
    state["llm_calls"] = state.get("llm_calls", 0) + 1
    return state


def final_agent(state: TravelState):
    final_prompt = f"""
    Finalize the travel response for the following.
    flights:
    {state['flight_results']}

    hotels:
    {state['hotel_results']}

    itinerary:
    {state['itinerary']}
    """      

    response = llm.invoke(
        input=[
            HumanMessage(content=final_prompt)
        ]
    )

    return {
        "message": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }

graph = StateGraph(TravelState)
graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)


graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)


_conn = psycopg.connect(DATABASE_URL, autocommit=True)
checkpoint = PostgresSaver(_conn)
checkpoint.setup()

app = graph.compile(checkpointer=checkpoint)

if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": "user_rahul"
        }
    }

    user_input = input("Enter your travel request: ")
    result = app.invoke(
        input={
            "message": [
                HumanMessage(content=user_input)
            ],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )

    print("Final Response:")
    
    for msg in result['message']:
        print(msg.content)