from mcp_ui_server import create_ui_resource

# Example 1: Direct HTML, delivered as text
resource1 = create_ui_resource({
    "uri": "ui://my-component/instance-1",
    "content": {
        "type": "rawHtml", 
        "htmlString": "<p>Hello World</p>"
    },
    "encoding": "text"
})

print("Resource 1:", resource1.model_dump_json(indent=2))