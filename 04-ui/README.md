# Adding mcp-ui

So we have a server, and we have a client, the client even uses an LLM, what else is there? Well, we can improve the response a bit, cause right now it's just sending text and responding with text. What if we want to send a nice UI with the response? This is where mcp-ui comes in. 

- Add mcp-ui to server response
- Render mcp-ui in VS Code
- Add mcp-ui to client rendering

## Install

```bash
uv "mcp[cli]" add mcp-ui-server
```

## Scaffold a client

```bash
npx create-vite@latest mcp-client --template react-ts
cd mcp-client
npm install
```

Install client depencencies:

```bash
npm install @mcp-ui/client @modelcontextprotocol/sdk @modelcontextprotocol/ext-apps
```

## How to create a UI tool

You use the `create_ui_resource` helper to create a resource with the appropriate structure for mcp-ui. The content can be any valid mcp-ui content, such as raw HTML, a chart definition, or an interactive component. Here's an example of a simple tool that returns a welcome message as raw HTML:

```python
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
```

## Add interaction

To add interaction, you can include buttons or other interactive elements in your mcp-ui content, and set up event handlers to respond to user actions. 

What we need to know is that your UI element is rendered inside an IFrame so that means it needs to communicate with parent window to trigger actions. You can use the `postMessage` API to send messages.

Here's an example of a tool that includes a button, and when the button is clicked, it sends a message back to the parent window:

```python
@mcp.tool()
def show_interactive_demo() -> list[UIResource]:
    """Show an interactive demo with buttons that send intents."""
    interactive_html = """
    <div style="padding: 20px; font-family: Arial, sans-serif;">
        <h2>Interactive Demo</h2>
        <p>Click the buttons below to send different types of actions back to the parent:</p>
        
        <div style="margin: 10px 0;">
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
```

We also need to ensure this meta information is populated so our receiving client gets the needed information. vHere's a helper we use for populating this information:

```python
def mark_ui_tool(tool_name: str):
    if tool_name in mcp._tool_manager._tools:
        tool = mcp._tool_manager._tools[tool_name]
        if hasattr(tool, "meta"):
            if not tool.meta:
                tool.meta = {}
            tool.meta["ui"] = {"isUITool": True}

```

and here's the call to mark the tool as a UI tool:

```python
mark_ui_tool("show_welcome")
```

### The client

The most important file on the client is `ToolUI.tsx`, this is where we render the mcp-ui content and handle the interactions.

When a message is posted from the IFrame it ends up in this handler:

```tsx
onUIAction={async (result) => {
    console.log('UI action:', result);
```

To call a tool in response to a UI action, we can use the `client.callTool` method:

```tsx
const { type } = result; 
    if (type === 'tool') {
    const { toolName: tn } = result.payload;
    const toolResult = await client.callTool({
        name: tn,
        arguments: result.payload.params,
    });
```

and because it's React, we can easily display the result in our component state:

```tsx
const blocks = (Array.isArray(toolResult?.content) ? toolResult.content : []);
const parsedResult = blocks[0]?.text ?? '';

console.log('Result from tool called by UI action:', parsedResult);

// setting the result in state to display in the UI
setResult(parsedResult);
```

Here's the visual parts of the component:

```tsx
<div style={{ marginTop: '8px', fontSize: '14px', color: '#333', border:"solid 1px grey", padding: '8px', borderRadius: '4px' }}><h2>Tool result: </h2> {result}</div>
```

## Exercise - add a droplist component

Add a component that renders a list of options, could be different types of credit cards and when the user selects one, it sends that information back to the parent window and calls a tool with the selected card type as an argument.

## Exercise - rebuild FAQ to leverage LLM

Currently the FAQ tool is doing a substring match, rebuild it to leverage the LLM, you can send the user question and the list of FAQs as context and ask the LLM to return the most relevant FAQ. This will make the FAQ tool much more powerful and flexible.