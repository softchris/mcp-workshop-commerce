# Workshop 03: Adding MCP UI

## 🎯 Learning Objectives

By the end of this workshop, you will:
- Understand what MCP UI is and why it's useful
- Create MCP tools that return rich UI components
- Build a React client that renders MCP UI resources
- Implement interactive UI elements that call back to MCP tools
- Handle communication between IFrames and parent windows

---

## 📚 Theory: Why MCP UI?

### The Problem
In previous workshops, we've been working with text-based interactions:
- Server responds with plain text
- Client displays the text
- Limited visual appeal and interactivity

### The Solution: MCP UI
MCP UI allows your MCP server to return **rich, interactive UI components** instead of plain text:
- 📊 Charts and visualizations
- 🎨 Custom HTML with styling
- 🔘 Interactive buttons and forms
- 🌐 Embedded external content
- 💬 Rich formatted content

### Architecture Overview
```
┌─────────────────┐         ┌──────────────────┐
│   MCP Server    │  ◄────► │  Client (React)  │
│                 │         │                  │
│  Python Tools   │         │  UIResourceRenderer
│  return UI      │         │  renders in IFrame │
│  Resources      │         │                  │
└─────────────────┘         └──────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │  IFrame (Sandbox) │
                            │  Renders HTML     │
                            │  postMessage API  │
                            └──────────────────┘
```

**Key Concept**: UI content is rendered in an **IFrame sandbox** for security. Communication happens via the `postMessage` API.

---

## 🛠️ Step 1: Environment Setup

### Install Server Dependencies

```bash
uv add "mcp[cli]" mcp-ui-server
```

**What this does**: 
- Adds MCP CLI tools to your project
- Adds `mcp-ui-server` package for creating UI resources

### Scaffold the React Client

```bash
npx create-vite@latest mcp-client --template react-ts
cd mcp-client
npm install
```

**Why Vite + React + TypeScript?**
- ⚡ Vite: Fast development server with HMR
- ⚛️ React: Component-based UI framework
- 📘 TypeScript: Type safety for MCP SDK

### Install Client Dependencies

```bash
npm install @mcp-ui/client @modelcontextprotocol/sdk @modelcontextprotocol/ext-apps
```

**Package breakdown**:
- `@mcp-ui/client`: UIResourceRenderer component for rendering MCP UI
- `@modelcontextprotocol/sdk`: Core MCP client SDK
- `@modelcontextprotocol/ext-apps`: Extended apps support

---

## 🎨 Step 2: Creating Your First UI Tool

### Understanding `create_ui_resource`

The `create_ui_resource` helper creates a properly formatted UI resource for MCP:

```python
from mcp_ui_server import create_ui_resource
```

### Example 1: Simple Welcome Message

**📍 CODE CALLOUT**: Look at `server.py` around line 90

```python
@mcp.tool()
def show_welcome():
    """Display a welcome message."""
    return create_ui_resource({
        "uri": "ui://welcome/main",        # Unique identifier for this UI
        "content": {
            "type": "rawHtml",              # Type of content
            "htmlString": "<h1>Welcome to My MCP Server!</h1><p>How can I help you today?</p>"
        },
        "encoding": "text"                  # Encoding format
    })
```

**Key Points**:
- `uri`: Must be unique and use `ui://` scheme
- `type: "rawHtml"`: Allows custom HTML/CSS/JS
- `encoding: "text"`: Specifies how content is encoded

### Example 2: External URL (Chart)

**📍 CODE CALLOUT**: Look at `server.py` around line 66

```python
@mcp.tool()
def show_live_chart():
    """Display a live-updating chart."""
    return create_ui_resource({
        "uri": "ui://live-chart/session-xyz",
        "content": {
            "type": "externalUrl",          # Embed external content
            "iframeUrl": chart_api_url      # URL to embed
        },
        "encoding": "blob"
    })
```

**When to use `externalUrl`**:
- Embedding third-party visualizations
- Displaying external dashboards
- Showing live data from APIs

---

## 🔄 Step 3: Adding Interactivity

### The Challenge: IFrame Communication

Your UI runs in an **isolated IFrame** (for security). To communicate with the parent:
- Use `window.parent.postMessage()` to send messages up
- Parent listens and can call MCP tools in response

### Interactive Button Example

**📍 CODE CALLOUT**: Check `server.py` for `show_interactive_demo` function

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
                    style="background: #059669; color: white; padding: 8px 16px; 
                           border: none; border-radius: 4px; margin: 5px; cursor: pointer;">
                Call Tool
            </button>
        </div>
        
        <div id="status" style="margin-top: 20px; padding: 10px; 
                                background: #f3f4f6; border-radius: 4px;">
            Ready - click a button to see the action
        </div>
    </div>
    
    <script>
        function sendToolCall(toolName, params) {
            const status = document.getElementById('status');
            status.innerHTML = `<strong>Tool call:</strong> ${toolName}<br>
                               <strong>Params:</strong> ${JSON.stringify(params)}`;
            
            // 🔑 KEY PART: Send message to parent window
            if (window.parent) {
                window.parent.postMessage({
                    type: 'tool',                    // Message type
                    payload: { 
                        toolName: toolName,          // Which tool to call
                        params: params               // Tool arguments
                    }
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

**Flow**:
1. User clicks button
2. JavaScript calls `sendToolCall()` 
3. `postMessage` sends data to parent window
4. React client receives message
5. Client calls MCP tool with parameters
6. Result displayed in UI

### Marking Tools as UI Tools

**Important**: You need to mark tools that return UI resources:

```python
def mark_ui_tool(tool_name: str):
    if tool_name in mcp._tool_manager._tools:
        tool = mcp._tool_manager._tools[tool_name]
        if hasattr(tool, "meta"):
            if not tool.meta:
                tool.meta = {}
            tool.meta["ui"] = {"isUITool": True}

# Mark your UI tools
mark_ui_tool("show_welcome")
mark_ui_tool("show_live_chart")
mark_ui_tool("show_interactive_demo")
```

**Why?** This metadata tells the client which tools return UI resources.

---

## ⚛️ Step 4: Client-Side Rendering

### The Core Component: ToolUI.tsx

**📍 CODE CALLOUT**: Open `mcp-client/src/ToolUI.tsx`

#### Key Part 1: Resource Extraction

```typescript
const contentBlocks = toolResult?.content ?? toolResult?.result?.content;
const resource = contentBlocks?.find((block: any) => block?.type === 'resource')?.resource;
```

**What's happening**: 
- Tool result contains content blocks
- Find the block with `type === 'resource'`
- Extract the resource object for rendering

#### Key Part 2: UIResourceRenderer

```tsx
<UIResourceRenderer
  resource={resource}
  htmlProps={{
    sandboxPermissions: 'allow-same-origin allow-scripts allow-forms allow-popups',
    autoResizeIframe: { height: true },
    style: { width: '100%', height: '200px', border: 'none' },
  }}
  onUIAction={async (result) => {
    // Handle messages from IFrame
  }}
/>
```

**Props explained**:
- `resource`: The UI resource from your MCP tool
- `htmlProps.sandboxPermissions`: IFrame sandbox settings
- `htmlProps.autoResizeIframe`: Auto-adjust height
- `onUIAction`: Handler for messages from IFrame

#### Key Part 3: Handling UI Actions

**📍 CODE CALLOUT**: Look at the `onUIAction` handler in `ToolUI.tsx` line 75

```tsx
onUIAction={async (result) => {
  console.log('UI action:', result);

  const { type } = result; 
  if (type === 'tool') {
    const { toolName: tn } = result.payload;

    setIsWaiting(true);
    try {
      // 🔑 Call the MCP tool
      const toolResult = await client.callTool({
        name: tn,
        arguments: result.payload.params,
      });

      // Extract text result
      const blocks = Array.isArray(toolResult?.content) ? toolResult.content : [];
      const parsedResult = blocks[0]?.text ?? '';

      console.log('Result from tool called by UI action:', parsedResult);
      
      // Update UI with result
      setResult(parsedResult);
    } finally {
      setIsWaiting(false);
    }
  }

  return { isError: false } as any;
}}
```

**Flow**:
1. Message received from IFrame via `postMessage`
2. Check if it's a 'tool' type message
3. Extract tool name and parameters
4. Call MCP tool using `client.callTool()`
5. Parse the response
6. Update React state to display result

#### Key Part 4: Displaying Results

```tsx
{isWaiting ? (
  <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
    Waiting for tool response...
  </div>
) : null}

<div style={{ marginTop: '8px', fontSize: '14px', color: '#333', 
              border: 'solid 1px grey', padding: '8px', borderRadius: '4px' }}>
  <h2>Tool result: </h2> {result}
</div>
```

**User feedback**:
- Show "Waiting..." while tool executes
- Display result in a styled container

---

## 🚀 Step 5: Running the System

### Start the MCP Server

```bash
cd 03-ui
uv run server.py
```

**Expected output**: Server running on port (check console)

### Start the React Client

```bash
cd mcp-client
npm run dev
```

**Expected output**: 
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Test the Flow

1. Open browser to `http://localhost:5173`
2. Call a UI tool (e.g., "show welcome")
3. See the UI render in the browser
4. For interactive tools: Click buttons and watch tool calls happen
5. Check browser console for debug logs

---

## 🎓 Exercise 1: Add a Dropdown Component

### Goal
Create an interactive dropdown that:
- Shows different credit card types (Visa, Mastercard, Amex, Discover)
- When user selects one, sends it to an MCP tool
- Tool returns card benefits/details

### Steps

#### 1. Create the Server Tool

Add to `server.py`:

```python
@mcp.tool()
def show_card_selector() -> list[UIResource]:
    """Display a credit card selector dropdown."""
    html = """
    <div style="padding: 24px; font-family: system-ui, sans-serif;">
        <h2 style="color: #1f2937; margin-bottom: 16px;">Select a Credit Card</h2>
        
        <select id="cardSelect" 
                style="width: 100%; padding: 10px; font-size: 16px; 
                       border: 2px solid #e5e7eb; border-radius: 6px;">
            <option value="">-- Choose a card --</option>
            <option value="visa">Visa</option>
            <option value="mastercard">Mastercard</option>
            <option value="amex">American Express</option>
            <option value="discover">Discover</option>
        </select>
        
        <div id="result" style="margin-top: 16px; padding: 12px; 
                                background: #f9fafb; border-radius: 6px; 
                                min-height: 40px;"></div>
    </div>
    
    <script>
        document.getElementById('cardSelect').addEventListener('change', (e) => {
            const cardType = e.target.value;
            if (!cardType) return;
            
            document.getElementById('result').innerHTML = 
                `<em>Getting info for ${cardType}...</em>`;
            
            // TODO: Send postMessage to parent
            // Hint: type should be 'tool'
            // Hint: toolName should be 'get_card_info'
            // Hint: params should include { cardType: cardType }
        });
    </script>
    """
    
    return [create_ui_resource({
        "uri": "ui://cards/selector",
        "content": {"type": "rawHtml", "htmlString": html},
        "encoding": "text"
    })]

@mcp.tool()
def get_card_info(cardType: str) -> str:
    """Get information about a credit card type."""
    cards = {
        "visa": "Visa: Worldwide acceptance, fraud protection, rewards program",
        "mastercard": "Mastercard: Global network, price protection, concierge service",
        "amex": "American Express: Premium rewards, travel benefits, purchase protection",
        "discover": "Discover: Cashback rewards, no annual fee, free credit score"
    }
    return cards.get(cardType, "Unknown card type")

# Don't forget to mark as UI tool!
mark_ui_tool("show_card_selector")
```

#### 2. Complete the postMessage Code

**Your task**: Fill in the `postMessage` call in the script section above.

**Hint**: Look at the interactive demo example for reference.

#### 3. Test It

1. Restart your server
2. Refresh the client
3. Call `show_card_selector`
4. Select a card from dropdown
5. Watch the result appear below!

---

## 🎓 Exercise 2: Rebuild FAQ with LLM

### Current Limitation

**📍 CODE CALLOUT**: Look at your FAQ tool in `server.py`

Currently, it probably does simple substring matching:

```python
def faq_tool(question: str) -> str:
    """Answer FAQ questions."""
    # Simple substring search
    for q, a in faq.items():
        if question.lower() in q.lower():
            return a
    return "No matching FAQ found"
```

**Problem**: 
- Only matches exact text
- Can't understand synonyms or paraphrasing
- Limited flexibility

### Enhancement: Use LLM for Smart Matching

**Goal**: Send the question + all FAQs to an LLM, let it find the best match.

#### The Approach

```python
from llm import call_llm  # Your LLM helper

@mcp.tool()
def smart_faq(question: str) -> str:
    """Answer FAQ questions using LLM-powered matching."""
    
    # Format FAQs as context
    faq_context = "\n".join([f"Q: {q}\nA: {a}\n" for q, a in faq.items()])
    
    # Create prompt
    prompt = f"""You are a helpful customer service assistant. 
    
Given the following FAQs:

{faq_context}

User question: {question}

Find the most relevant FAQ and return the answer. If no FAQ matches, 
say "I don't have information about that in our FAQ."

Answer:"""

    # Call LLM
    response = call_llm(prompt)
    return response
```

#### Your Tasks

1. **Implement the smart_faq tool** with LLM integration
2. **Create a UI for it** that shows:
   - Input field for question
   - Submit button
   - Result display area
3. **Compare results**: Try the same question with old vs new FAQ
4. **Test edge cases**:
   - Paraphrased questions
   - Questions with typos
   - Related but not exact questions

#### Bonus Challenge

Add **streaming responses**: Show the LLM response as it's being generated, not all at once!

---

## 🎯 Key Takeaways

### Architecture
- ✅ MCP servers can return UI resources, not just text
- ✅ UI renders in isolated IFrame for security
- ✅ Communication via `postMessage` API

### Server-Side
- ✅ Use `create_ui_resource()` to format UI responses
- ✅ Support `rawHtml` and `externalUrl` content types
- ✅ Mark tools with UI meta flag
- ✅ Handle tool calls triggered from UI

### Client-Side
- ✅ `UIResourceRenderer` handles rendering
- ✅ `onUIAction` receives messages from IFrame
- ✅ Use `client.callTool()` to invoke MCP tools
- ✅ Manage state for loading and results

### Best Practices
- 🔒 Always use IFrame sandboxing
- 📝 Add clear debug logging
- 🎨 Style your UI components nicely
- ⚡ Show loading states during tool calls
- 🐛 Handle errors gracefully

---

## 🔍 Debugging Tips

### Server Issues

1. **Tool not returning UI?**
   - Check `create_ui_resource` format
   - Verify URI uses `ui://` scheme
   - Ensure tool is marked as UI tool

2. **IFrame not rendering?**
   - Check CORS settings
   - Verify HTML syntax
   - Look for JavaScript errors in browser console

### Client Issues

1. **UI action not triggering?**
   - Check `postMessage` format
   - Verify `onUIAction` handler
   - Look at browser DevTools console

2. **Tool call failing?**
   - Check tool name spelling
   - Verify parameters match tool signature
   - Check MCP server logs

### General

- Always check **both** browser console and server terminal
- Use `console.log()` liberally during development
- Test with simple examples before complex ones

---

## 📚 Additional Resources

- MCP UI Documentation: https://spec.modelcontextprotocol.io/ui/
- React Documentation: https://react.dev
- IFrame postMessage: https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage

---

## ✨ Next Steps

After completing this workshop:
1. Experiment with more complex UI components (forms, tables, charts)
2. Try integrating real APIs for external content
3. Add authentication/authorization to your tools
4. Build a multi-tool dashboard that combines several UI tools

Happy coding! 🚀
