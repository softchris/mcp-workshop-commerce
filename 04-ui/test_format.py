#!/usr/bin/env python3
"""Test if the new tool output format works correctly."""

import json
from mcp.types import TextResourceContents, AnnotatedContent


def test():
    """Test the server tool output format."""
    
    # Test the AnnotatedContent format locally
    result = AnnotatedContent(
        type="resource",
        resource=TextResourceContents(
            uri="ui://welcome/main",
            mimeType="text/html",
            text="<h1>Welcome to My MCP Server!</h1><p>How can I help you today?</p>"
        )
    )
    
    print("Tool output format:")
    print(json.dumps(result.model_dump(), indent=2, default=str))
    print()
    print("This format should work with AppRenderer")


if __name__ == "__main__":
    test()
