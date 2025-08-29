# CASE: Advanced Investment Analysis Agent

This project demonstrates a sophisticated multi-agent system for generating investment analysis reports. It integrates several key concepts:
- **Multi-Agent Collaboration:** Uses LangGraph to coordinate between a planner, researchers, and a report writer.
- **Long & Short-Term Memory:** Manages conversation state and persists final reports in a vector database.
- **Custom Tools:** Agents use tools to fetch financial data and perform web searches.
- **Human-in-the-Loop:** A Gradio UI allows users to provide feedback on generated reports.
- **Automated Validation:** Uses the Ragas framework to automatically score the factual consistency of the reports.

## Setup

1.  **API Keys:** This application requires an API key for a large language model. Please set it as an environment variable. For example, for Dashscope Qwen:
    ```bash
    export DASHSCOPE_API_KEY="your_api_key_here"
    ```

2.  **Install Dependencies:** Navigate to this directory and install the required packages.
    ```bash
    cd CASE-Advanced-Investment-Agent
    pip install -r requirements.txt
    ```

## How to Run

1.  **Start the Application:**
    ```bash
    python main_app.py
    ```
2.  **Open the UI:** Open your web browser and navigate to the local URL provided by Gradio (usually `http://127.0.0.1:7860`).
3.  **Use the App:**
    - Enter a company name (e.g., "NVIDIA", "Apple") and click "Run Analysis".
    - View the generated report and the Ragas "Confidence Score".
    - Provide your feedback in the text box and click "Submit Feedback".
