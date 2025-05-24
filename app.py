# main.py

%%capture --no-stderr
%pip install -U langgraph langchain_community "langchain[openai]"
%pip install -q langchain-google-genai

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from typing import Literal

import requests
from prompts import get_system_prompt, get_generate_query_prompt, get_check_query_prompt

# --- Set up Gemini
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",
    temperature=0.7,
    google_api_key="YOUR_GOOGLE_API_KEY",  # Replace with actual key
    convert_system_message_to_human=True
)

# --- Download DB
url = "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db"
r = requests.get(url)
with open("Chinook.db", "wb") as f:
    f.write(r.content)

# --- Setup DB
db = SQLDatabase.from_uri("sqlite:///Chinook.db")
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()

# --- Get system prompt
system_prompt = get_system_prompt(db.dialect)

agent = create_react_agent(
    llm,
    tools,
    prompt=system_prompt,
)

# --- Manual Test (Optional)
question = "Which sales agent made the most in sales in 2009?"
for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()

# --- Build LangGraph Agent (multi-step)

get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
run_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")

get_schema_node = ToolNode([get_schema_tool], name="get_schema")
run_query_node = ToolNode([run_query_tool], name="run_query")

def list_tables(state: MessagesState):
    tool_call = {"name": "sql_db_list_tables", "args": {}, "id": "abc123", "type": "tool_call"}
    tool_call_message = AIMessage(content="", tool_calls=[tool_call])
    list_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
    result = list_tool.invoke(tool_call)
    response = AIMessage(content=f"Available tables: {result.content}")
    return {"messages": [tool_call_message, result, response]}

def call_get_schema(state: MessagesState):
    llm_with_tools = llm.bind_tools([get_schema_tool], tool_choice="any")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def generate_query(state: MessagesState):
    sys_msg = {"role": "system", "content": get_generate_query_prompt(db.dialect)}
    llm_with_tools = llm.bind_tools([run_query_tool])
    response = llm_with_tools.invoke([sys_msg] + state["messages"])
    return {"messages": [response]}

def check_query(state: MessagesState):
    sys_msg = {"role": "system", "content": get_check_query_prompt(db.dialect)}
    tool_call = state["messages"][-1].tool_calls[0]
    user_msg = {"role": "user", "content": tool_call["args"]["query"]}
    llm_with_tools = llm.bind_tools([run_query_tool], tool_choice="any")
    response = llm_with_tools.invoke([sys_msg, user_msg])
    response.id = state["messages"][-1].id
    return {"messages": [response]}

def should_continue(state: MessagesState) -> Literal[END, "check_query"]:
    return "check_query" if state["messages"][-1].tool_calls else END

builder = StateGraph(MessagesState)
builder.add_node(list_tables)
builder.add_node(call_get_schema)
builder.add_node(get_schema_node, "get_schema")
builder.add_node(generate_query)
builder.add_node(check_query)
builder.add_node(run_query_node, "run_query")

builder.add_edge(START, "list_tables")
builder.add_edge("list_tables", "call_get_schema")
builder.add_edge("call_get_schema", "get_schema")
builder.add_edge("get_schema", "generate_query")
builder.add_conditional_edges("generate_query", should_continue)
builder.add_edge("check_query", "run_query")
builder.add_edge("run_query", "generate_query")

agent = builder.compile()

# --- Optional visualization (for Colab)
from IPython.display import Image, display
display(Image(agent.get_graph().draw_mermaid_png()))

# --- Ask question
question = "Which sales agent made the most in sales in 2009?"
for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()
