from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP('test')

@mcp.tool()
def show_welcome():
    'Display a welcome message.'
    return 'Welcome!'

# Add metadata
def add_ui_metadata(tool_name: str, resource_uri: str):
    if tool_name in mcp._tool_manager._tools:
        tool = mcp._tool_manager._tools[tool_name]
        if hasattr(tool, 'meta'):
            if not tool.meta:
                tool.meta = {}
            tool.meta['ui'] = {'resourceUri': resource_uri}

add_ui_metadata('show_welcome', 'ui://welcome/main')

# Check what's in the tool
tool = mcp._tool_manager._tools['show_welcome']
print('After metadata registration:')
print('tool.meta:', tool.meta)
print()
print('Tool serialized:')
print(json.dumps(tool.model_dump(), indent=2, default=str))
