import argparse
from time import ctime
from mcp.server.fastmcp import FastMCP
from mcp_ui_server import create_ui_resource

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path

from llm import call_llm

from mcp_ui_server.core import UIResource

# Create FastMCP instance
mcp = FastMCP("my-server")

# Configure settings BEFORE creating the app
mcp.settings.streamable_http_path = "/mcp"
mcp.settings.stateless_http = True

# 2. Get the ASGI app from FastMCP
# mcp_app = mcp.asgi_app()
# mcp_app = mcp.sse_app()
mcp_app = mcp.streamable_http_app()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # mcp.web (or similar) handles the lifecycle, but we hook into it manually
    # because we are mounting mcp_app instead of running it directly.
    async with mcp._session_manager.run():
        yield

app = FastAPI(lifespan=lifespan)

SANDBOX_PROXY_PATH = (
    Path(__file__).resolve().parent / "mcp-client" / "public" / "sandbox_proxy.html"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite / React
        "http://localhost:5174",   # Vite / React alternative port
        "https://mcpui.dev",       # your deployed UI
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/sandbox_proxy.html")
def sandbox_proxy():
    """Serve the sandbox proxy from a different origin than the UI host."""
    return FileResponse(SANDBOX_PROXY_PATH)


chart_api_url = "https://quickchart.io/chart?c={type:'bar',data:{labels:[2012,2013,2014,2015, 2016],datasets:[{label:'Users',data:[120,60,50,180,120]}]}}"

@mcp.tool()
def show_live_chart():
    """Display a live-updating chart."""
    return create_ui_resource({
    "uri": "ui://live-chart/session-xyz",
    "content": {
        "type": "externalUrl", 
        "iframeUrl": chart_api_url
    },
    "encoding": "blob"
})

@mcp.tool()
def show_dashboard():
    """Display an analytics dashboard."""
    return create_ui_resource({
        "uri": "ui://dashboard/analytics",
        "content": {
            "type": "externalUrl",
            "iframeUrl": "https://www.ellos.se/"
        },
        "encoding": "text"
    })

@mcp.tool()
def show_welcome():
    """Display a welcome message."""
    return create_ui_resource({
        "uri": "ui://welcome/main",
        "content": {
            "type": "rawHtml",
            "htmlString": "<h1>Welcome to My MCP Server!</h1><p>How can I help you today?</p>"
        },
        "encoding": "text"
    })


# faq e-commerce
faq = {
    "What is your return policy?": "Our return policy allows you to return items within 30 days of purchase for a full refund. Please ensure that the items are in their original condition and packaging.",    
    "Do you offer international shipping?": "Yes, we offer international shipping to select countries. Shipping fees and delivery times vary based on the destination. Please check our shipping information page for details.",
    "How can I track my order?": "Once your order has been shipped, you will receive a tracking number via email. You can use this number to track your order on our website or through the carrier's tracking system.",
    "What payment methods do you accept?": "We accept a variety of payment methods including credit/debit cards, PayPal, and Apple Pay. All payments are processed securely through our payment gateway.",
    "How do I contact customer support?": "You can contact our customer support team via email at support@example.com."
}

@mcp.tool(description="Run faq question with LLM")
async def ask_question_llm(question: str) -> str:
    # Use LLM to find the most relevant FAQ answer
    context = "\n".join([f"Q: {q}\nA: {a}" for q, a in faq.items()])
    prompt = f"{context}\n\nQ: {question}\nA:"
    answer = await call_llm(prompt)
    return answer

@mcp.tool(description="Run faq question")
def ask_question(question: str) -> str:
    # substring match to find relevant FAQ answer
    for q, a in faq.items():
        if question.lower() in q.lower():
            return a
    return "Sorry, I don't have an answer to that question. Please contact support for more help."

@mcp.tool(description="Show interactive faq") 
def show_faq() -> list[UIResource]:
    faq = """
    <div style="padding: 20px; font-family: Arial, sans-serif;">
        <h2>FAQ</h2>
        <p>Ask your questions here!</p>
        <input type="text" id="question" placeholder="Type your question..." style="padding: 8px; width: 80%; margin-right: 8px; border: 1px solid #ccc; border-radius: 4px;">
        <button onclick="sendQuestion()" style="background: #2563eb; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer;">
            Ask MCP
        </button>
    </div>
    <script>
        function sendQuestion() {
            const questionInput = document.getElementById('question');
            const question = questionInput.value;
            if (window.parent) {
                window.parent.postMessage({
                    type: 'tool',
                    payload: { toolName: 'ask_question_llm', params: { question: question } }
                }, '*');
            }
        }
    </script>
    """

    ui_resource = create_ui_resource({
        "uri": "ui://faq/interactive",
        "content": {
            "type": "rawHtml",
            "htmlString": faq
        },
        "encoding": "text"
    })
    return [ui_resource]



@mcp.tool()
def show_interactive_demo() -> list[UIResource]:
    """Show an interactive demo with buttons that send intents."""
    interactive_html = """
    <div style="padding: 20px; font-family: Arial, sans-serif;">
        <h2>Interactive Demo</h2>
        <p>Click the buttons below to send different types of actions back to the parent:</p>
        
        <div style="margin: 10px 0;">
            <button onclick="sendIntent('user_action', {type: 'button_click', id: 'demo'})" 
                    style="background: #2563eb; color: white; padding: 8px 16px; border: none; border-radius: 4px; margin: 5px; cursor: pointer;">
                Send Intent
            </button>
            <button onclick="sendToolCall('get_data', {source: 'ui'})" 
                    style="background: #059669; color: white; padding: 8px 16px; border: none; border-radius: 4px; margin: 5px; cursor: pointer;">
                Call Tool
            </button>
        </div>
        
        <div id="status" style="margin-top: 20px; padding: 10px; background: #f3f4f6; border-radius: 4px;">
            Ready - click a button to see the action
        </div>
    </div>
    
    <script>
        function sendIntent(intent, params) {
            const status = document.getElementById('status');
            status.innerHTML = `<strong>Intent sent:</strong> ${intent}<br><strong>Params:</strong> ${JSON.stringify(params)}`;
            
            if (window.parent) {
                window.parent.postMessage({
                    type: 'intent',
                    payload: { intent: intent, params: params }
                }, '*');
            }
        }
        
        function sendToolCall(toolName, params) {
            const status = document.getElementById('status');
            status.innerHTML = `<strong>Tool call:</strong> ${toolName}<br><strong>Params:</strong> ${JSON.stringify(params)}`;
            
            if (window.parent) {
                window.parent.postMessage({
                    type: 'tool',
                    payload: { toolName: toolName, params: params }
                }, '*');
            }
        }
    </script>
    """
    
    ui_resource = create_ui_resource({
        "uri": "ui://demo/interactive",
        "content": {
            "type": "rawHtml",
            "htmlString": interactive_html
        },
        "encoding": "text"
    })
    return [ui_resource]


@mcp.tool(description="A tool to receive data from the interactive demo")
def get_data(source: str):
    print(f"Received tool call from {source}!")
    """A tool that can be called from the UI to demonstrate interactivity."""
    print(f"Received tool call from {source}!")
    return f"Data received from {source} at {ctime()}"

# Mark tools as UI-capable (no resourceUri since content is embedded)
def mark_ui_tool(tool_name: str):
    if tool_name in mcp._tool_manager._tools:
        tool = mcp._tool_manager._tools[tool_name]
        if hasattr(tool, "meta"):
            if not tool.meta:
                tool.meta = {}
            tool.meta["ui"] = {"isUITool": True}

mark_ui_tool("show_dashboard")
mark_ui_tool("show_welcome")
mark_ui_tool("show_live_chart")
mark_ui_tool("show_interactive_demo")
mark_ui_tool("show_faq")

# Mount the MCP app at root to avoid double path issues
app.mount("/", mcp_app)

if __name__ == "__main__":
    import uvicorn
    # Debug routes
    for route in app.routes:
        print(f"Route: {route.path} -> {route.name}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)