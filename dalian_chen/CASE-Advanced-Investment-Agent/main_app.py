import os
import uuid
import json
import pandas as pd
from datetime import datetime
from typing import List, TypedDict, Annotated, Dict
import operator

import gradio as gr
from bs4 import BeautifulSoup
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.vectorstores import Chroma
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.llms import Tongyi

from langgraph.graph import StateGraph, END

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from datasets import Dataset

# --- 1. Environment and Configuration ---
# Make sure to set your DASHSCOPE_API_KEY in your environment variables
if "DASHSCOPE_API_KEY" not in os.environ:
    os.environ["DASHSCOPE_API_KEY"] = "YOUR_API_KEY"

# --- 2. RAG and Knowledge Base Setup ---
# This will be our internal knowledge base for the RAG function
knowledge_base_vectorstore = Chroma(
    collection_name="internal_knowledge",
    embedding_function=DashScopeEmbeddings(model="text-embedding-v2"),
    persist_directory="./chroma_db_knowledge"
)

def setup_knowledge_base():
    """
    Pre-loads the knowledge base with some sample documents.
    This function is called once at startup.
    """
    print("---Setting up Knowledge Base---")
    # Check if the knowledge base is already populated
    if knowledge_base_vectorstore._collection.count() > 0:
        print("---Knowledge Base already contains data. Skipping setup.---")
        return

    sample_docs = [
        ("NVIDIA AI Dominance", "NVIDIA's recent earnings report for Q4 2024 showed a 265% increase in revenue, largely driven by its H100 GPUs for data centers. The company's CUDA software platform creates a strong competitive moat, making it difficult for competitors to gain market share."),
        ("Apple Services Growth", "Apple's services division, which includes the App Store, Apple Music, and iCloud, has become a major revenue driver. In the last fiscal year, services accounted for over 25% of total revenue, showing a strategic shift from hardware dependency."),
        ("Semiconductor Industry Trends 2025", "The semiconductor industry is facing a cyclical downturn in consumer electronics but is seeing massive growth in the automotive and AI sectors. Companies specializing in custom AI accelerators are poised for significant growth."),
    ]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs_to_add = []
    for title, content in sample_docs:
        splits = text_splitter.create_documents([content], metadatas=[{"source": title}])
        docs_to_add.extend(splits)

    knowledge_base_vectorstore.add_documents(docs_to_add)
    print(f"---Knowledge Base setup complete. Added {len(docs_to_add)} document chunks.---")

# --- 3. Tools Definition ---
@tool
def query_knowledge_base(query: str) -> str:
    """
    Queries the internal knowledge base for relevant information on a company or topic.
    Use this tool first to gather internal intelligence before searching the web.
    """
    print(f"---TOOL: Querying Knowledge Base for: {query}---")
    retriever = knowledge_base_vectorstore.as_retriever(search_kwargs={"k": 2})
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant information found in the internal knowledge base."
    return "\n---\n".join([f"Source: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}" for doc in docs])

@tool
def fetch_stock_data(company_name: str) -> str:
    """
    Fetches simulated financial data for a given company.
    In a real application, this would call a financial API.
    """
    print(f"---TOOL: Fetching financial data for {company_name}---")
    # Simulate API call
    if "nvidia" in company_name.lower():
        data = {"company": "NVIDIA", "ticker": "NVDA", "price": 950.00, "p_e_ratio": 75.0, "market_cap_trillions": 2.3, "analyst_rating": "Strong Buy"}
    elif "apple" in company_name.lower():
        data = {"company": "Apple Inc.", "ticker": "AAPL", "price": 190.00, "p_e_ratio": 30.0, "market_cap_trillions": 2.9, "analyst_rating": "Buy"}
    else:
        data = {"company": company_name, "ticker": "UNKNOWN", "price": 100.00, "p_e_ratio": 20.0, "market_cap_trillions": 0.5, "analyst_rating": "Hold"}
    return json.dumps(data)

# Web search tool
web_search_tool = DuckDuckGoSearchRun()

# List of all tools available to the agents
all_tools = [query_knowledge_base, fetch_stock_data, web_search_tool]

# --- 4. Graph State Definition ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    plan: str
    research_data: Annotated[Dict[str, str], operator.add]
    report: str
    report_id: str

# --- 5. LLM and Embeddings Initialization ---
llm = Tongyi(model_name="qwen-long")
embeddings = DashScopeEmbeddings(model="text-embedding-v2")

# --- 6. Long-Term Memory (Vector Store for past reports) ---
report_vectorstore = Chroma(
    collection_name="investment_reports",
    embedding_function=embeddings,
    persist_directory="./chroma_db_reports"
)
report_retriever = report_vectorstore.as_retriever(search_kwargs={"k": 1})

# --- 7. Agent and Graph Node Definitions ---

def create_agent(llm: Tongyi, tools: list, system_prompt: str) -> Runnable:
    """Factory function to create a new agent runnable."""
    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{input}")])
    return prompt | llm.bind_tools(tools)

def call_tools(state: AgentState) -> dict:
    """Function to execute tools called by the agent."""
    tool_calls = state["messages"][-1].tool_calls
    if not tool_calls:
        return {}

    tool_outputs = []
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        print(f"---Executing Tool: {tool_name} with args: {tool_args}---")
        try:
            tool_to_call = next(t for t in all_tools if t.name == tool_name)
            output = tool_to_call.invoke(tool_args)
            tool_outputs.append(ToolMessage(content=str(output), tool_call_id=tool_call["id"]))
        except Exception as e:
            print(f"Error executing tool {tool_name}: {e}")
            tool_outputs.append(ToolMessage(content=f"Error: {e}", tool_call_id=tool_call["id"]))

    # Aggregate research data
    new_data = {tool_call["name"]: str(output) for tool_call, output in zip(tool_calls, tool_outputs)}
    return {"messages": tool_outputs, "research_data": new_data}


def coordinator_node(state: AgentState) -> dict:
    """
The first node in the graph. It checks long-term memory and creates a plan.
    """
    query = state["messages"][0].content
    print(f"---Coordinator: Received query: {query}---")

    # Check long-term memory for past reports
    docs = report_retriever.invoke(query)
    if docs:
        existing_report = docs[0].page_content
        print("---Coordinator: Found similar report in long-term memory.---")
        return {"report": existing_report, "messages": state["messages"] + [AIMessage(content="Found a relevant report in memory.")]}

    # If no report found, create a plan
    print("---Coordinator: No similar report found. Creating a new plan.---")
    planner_prompt = """You are the expert coordinator of a financial analysis team.
    Your job is to create a step-by-step research plan based on the user's request.
    The plan MUST follow this sequence:
    1.  **Internal Knowledge Query**: Use the `query_knowledge_base` tool to see what our internal system already knows.
    2.  **Financial Data**: Use the `fetch_stock_data` tool to get quantitative metrics.
    3.  **News Analysis**: Use the `search` tool to find recent news, analyst opinions, and market sentiment.

    Create a concise, actionable plan based on this three-step process.
    """
    planner_agent = create_agent(llm, all_tools, planner_prompt)
    response = planner_agent.invoke({"input": query})

    return {
        "plan": response.content,
        "messages": state["messages"] + [AIMessage(content=f"Plan created: {response.content}")]
    }

def research_node(state: AgentState) -> dict:
    """
    Executes the research plan by calling the necessary tools.
    """
    plan = state["plan"]
    print(f"---Researcher: Executing plan: {plan}---")

    researcher_prompt = f"""You are a diligent researcher. Your task is to execute the given plan by calling the correct tools.
    Do not make up information. Call the tools with the exact company name provided in the user's query.
    Plan: {plan}
    User Query: {state['messages'][0].content}
    """
    researcher_agent = create_agent(llm, all_tools, researcher_prompt)
    response = researcher_agent.invoke({"input": state['messages'][0].content})

    return {"messages": state["messages"] + [response]}


def report_writer_node(state: AgentState) -> dict:
    """
    Synthesizes the research data into a final report.
    """
    print("---Report Writer: Synthesizing data into a report.---")
    research_summary = "\n\n".join([f"### Source: {key}\n{value}" for key, value in state["research_data"].items()])

    writer_prompt = f"""You are a professional financial analyst.
    Your task is to write a clear, concise, and well-structured investment analysis report based on the provided data.
    The report should have the following sections:
    1.  **Internal Knowledge Summary:** Key findings from our internal knowledge base.
    2.  **Quantitative Analysis:** Based on the financial data.
    3.  **Qualitative Analysis:** Based on the news and market sentiment.
    4.  **Conclusion & Recommendation:** Your final opinion, synthesizing all available information.

    Do not include any information that is not present in the research data.
    Research Data:
    {research_summary}
    """
    writer_agent = create_agent(llm, [], writer_prompt) # No tools for the writer
    response = writer_agent.invoke({"input": ""})

    report_id = str(uuid.uuid4())
    return {"report": response.content, "report_id": report_id}


# --- 8. Graph Edges and Conditional Logic ---

def should_continue(state: AgentState) -> str:
    """Conditional edge to decide the next step."""
    if state.get("report"):
        return "end"
    if state["messages"][-1].tool_calls:
        return "call_tools"
    if state.get("plan") and not state.get("research_data"):
        return "research"
    # This condition allows for multiple research steps if needed, but our current plan is one-shot.
    # For a more complex plan, you might need a loop.
    return "write_report"


# --- 9. Graph Definition and Compilation ---

graph_builder = StateGraph(AgentState)

graph_builder.add_node("coordinator", coordinator_node)
graph_builder.add_node("research", research_node)
graph_builder.add_node("call_tools", call_tools)
graph_builder.add_node("write_report", report_writer_node)

graph_builder.set_entry_point("coordinator")

graph_builder.add_conditional_edges(
    "coordinator",
    lambda x: "end" if x.get("report") else "research",
    {"research": "research", "end": END}
)
graph_builder.add_edge("research", "call_tools")
graph_builder.add_edge("call_tools", "write_report")
graph_builder.add_edge("write_report", END)

graph = graph_builder.compile()


# --- 10. Ragas Validation and Human Feedback ---

def validate_with_ragas(query, report, research_data):
    """Uses Ragas to evaluate the generated report."""
    print("---RAGAS: Starting validation...")
    contexts = [str(v) for v in research_data.values()]
    if not contexts:
        return {"faithfulness": 0, "answer_relevancy": 0, "details": "No context to evaluate."}

    dataset_dict = {"question": [query], "answer": [report], "contexts": [contexts]}
    dataset = Dataset.from_dict(dataset_dict)

    result = evaluate(dataset, metrics=[faithfulness, answer_relevancy], llm=llm, embeddings=embeddings)
    print(f"---RAGAS: Validation complete. Score: {result}")
    return result


def save_to_long_term_memory(report_id, report, query, ragas_score, feedback=""):
    """Saves the final report and metadata to the report vector store."""
    print(f"---Memory: Saving report {report_id} to ChromaDB.")
    metadata = {
        "report_id": report_id,
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "ragas_faithfulness": ragas_score.get('faithfulness', 0),
        "ragas_relevancy": ragas_score.get('answer_relevancy', 0),
        "user_feedback": feedback
    }
    report_vectorstore.add_texts(texts=[report], ids=[report_id], metadatas=[metadata])
    print("---Memory: Save complete.---")


# --- 11. Gradio UI ---

def run_analysis(query: str):
    """The main function called by the Gradio interface."""
    if not query:
        return "Please enter a company name.", "", None, ""

    initial_state = {"messages": [HumanMessage(content=query)], "research_data": {}}
    final_state = graph.invoke(initial_state)

    report = final_state["report"]
    report_id = final_state.get("report_id", str(uuid.uuid4()))
    research_data = final_state["research_data"]

    ragas_score = validate_with_ragas(query, report, research_data)
    confidence_score = (ragas_score.get('faithfulness', 0) + ragas_score.get('answer_relevancy', 0)) / 2
    confidence_text = f"Confidence Score: {confidence_score:.2f} (Faithfulness: {ragas_score.get('faithfulness', 0):.2f}, Relevancy: {ragas_score.get('answer_relevancy', 0):.2f})"

    save_to_long_term_memory(report_id, report, query, ragas_score)

    return report, confidence_text, report_id, query

def handle_feedback(report_id: str, query: str, report: str, feedback: str):
    """Handles the user feedback submission."""
    if not report_id or not feedback:
        return "Feedback submission failed. Report ID or feedback is missing."

    print(f"---Feedback: Received for report {report_id}: {feedback}---")
    feedback_log_file = "feedback_log.jsonl"
    log_entry = {
        "report_id": report_id,
        "query": query,
        "report": report,
        "feedback": feedback,
        "timestamp": datetime.now().isoformat()
    }
    with open(feedback_log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return f"Feedback received for Report ID: {report_id}. Thank you!"


with gr.Blocks(theme=gr.themes.Soft(), title="Advanced Investment Analysis Agent with RAG") as demo:
    gr.Markdown("# Advanced Investment Analysis Agent with RAG")
    gr.Markdown("This demo uses a multi-agent system that first queries an internal knowledge base (RAG) before searching the web to generate a report.")

    report_id_state = gr.State()
    query_state = gr.State()
    report_state = gr.State()

    with gr.Row():
        with gr.Column(scale=1):
            query_input = gr.Textbox(label="Enter Company Name", placeholder="e.g., NVIDIA")
            run_button = gr.Button("Run Analysis", variant="primary")
            confidence_output = gr.Textbox(label="RAGAs Validation", interactive=False)

        with gr.Column(scale=2):
            report_output = gr.Markdown(label="Generated Report")

    with gr.Row():
        with gr.Column():
            gr.Markdown("---")
            gr.Markdown("### Human Feedback")
            feedback_input = gr.Textbox(label="Provide feedback or corrections on the report above", placeholder="e.g., The P/E ratio seems too high.")
            feedback_button = gr.Button("Submit Feedback")
            feedback_status = gr.Textbox(label="Feedback Status", interactive=False)

    run_button.click(
        fn=run_analysis,
        inputs=[query_input],
        outputs=[report_output, confidence_output, report_id_state, query_state]
    ).then(
        lambda report: report,
        inputs=[report_output],
        outputs=[report_state]
    )

    feedback_button.click(
        fn=handle_feedback,
        inputs=[report_id_state, query_state, report_state, feedback_input],
        outputs=[feedback_status]
    )

if __name__ == "__main__":
    # Setup the knowledge base on startup
    setup_knowledge_base()
    print("Starting Gradio UI... Open at http://127.0.0.1:7860")
    demo.launch()