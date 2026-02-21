# Workshop Step-by-Step Script: Search and FAQ Tools with MCP

## Introduction (2-3 minutes)
"Welcome! Today we're building an MCP server with search and FAQ tools for an e-commerce website. By the end, you'll understand how to create tools that GitHub Copilot can use."

---

## Step 1: Project Setup (5 minutes)

**Say:** "First, let's set up our Python environment."

1. **Initialize the project:**

   ```powershell
   uv init
   ```

   *Alternative for those without uv:*
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```powershell
   uv add "mcp[cli]"
   ```
   *Alternative:*
   ```powershell
   pip install "mcp[cli]"
   ```

**Checkpoint:** "Everyone should now have their environment ready."

---

## Step 2: Understanding the Server Features (3 minutes)

**Say:** "Our MCP server will have two main tools:"

- **Search Tool** - Filter products by:
  - Price
  - Color
  - Name

- **FAQ Tool** - Provide support resources

**Show the diagram:** (if presenting the mermaid chart)

## Step 3: Start the Server (5 minutes)

**Say:** "Now let's start our MCP server."

1. **Run the server:**
   ```powershell
   mcp run server.py
   ```

2. **Verify:** "You should see the server starting on `http://127.0.0.1:8000/mcp`"

---

## Step 4: Configure VS Code (5 minutes)

**Say:** "To use this server with GitHub Copilot, we need to register it in VS Code."

1. **Create or open** `.vscode/mcp.json`

2. **Add this configuration:**
   ````json
   {
       "servers": {
           "my-mcp-server-414ca0bf": {
               "url": "http://127.0.0.1:8000/mcp",
               "type": "http"
           }
       },
       "inputs": []
   }
   ````

**Checkpoint:** "Everyone should now have the server registered."

---

## Step 5: Test with GitHub Copilot Chat (10-15 minutes)

**Say:** "Let's test our tools with GitHub Copilot Chat. Open the Chat panel and try these prompts."

### Test 1: Specific Product Search
**Prompt:** "show me navy sweater under 100, use a tool"

**Expected Result:**
```text
Wool Sweater - $79.99 (navy)
```

**Explain:** "Notice how Copilot called our search tool and filtered by both color and price."

---

### Test 2: Price Filter
**Prompt:** "show me items under 100, use a tool"

**Expected Result:**
```text
Cotton T-Shirt - $19.99 (red)
Denim Jeans - $49.99 (blue)
Wool Sweater - $79.99 (navy)
Summer Dress - $39.99 (floral)
Silk Blouse - $89.99 (white)
Cargo Shorts - $29.99 (khaki)
Athletic Hoodie - $59.99 (green)
```

**Explain:** "The search tool filtered all products under $100."

---

### Test 3: FAQ Tool
**Prompt:** "Tell me about shipping in your FAQ"

**Expected Result:**
```text
Yes, we offer international shipping to select countries. Shipping fees and delivery times vary based on the destination.
```

**Explain:** "This demonstrates the FAQ tool retrieving support information."

---

## Step 6: Discussion and Q&A (5 minutes)

**Say:** "This is great for using GitHub Copilot Chat, but what if we want to build our own client?"

**Key Points:**
- MCP servers expose tools that AI can use
- GitHub Copilot is one client, but we can build custom clients
- Next step: Build a custom client that calls this server

**Questions to ask participants:**
- "What other tools could you imagine adding to this server?"
- "How might you use this in your own projects?"

---

## Wrap Up

**Say:** "You've successfully created an MCP server with search and FAQ tools! The server is running and GitHub Copilot can use these tools to help users find products and get support information."

**Next Steps:** "In the next part, we'll build a custom client that can call this server programmatically."

---

## Troubleshooting Tips

**If server won't start:**
- Check Python version (3.10+)
- Verify dependencies installed
- Check port 8000 isn't in use

**If Copilot can't find tools:**
- Verify mcp.json is in .vscode folder
- Reload VS Code window
- Check server is running

**If results are unexpected:**
- Review the prompt wording
- Explicitly say "use a tool"
- Check server logs for errors
