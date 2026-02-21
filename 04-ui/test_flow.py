#!/usr/bin/env python3
"""Test calling tools and fetching resources through the MCP server."""

import asyncio
import json
import aiohttp


async def test():
    """Test the full workflow."""
    async with aiohttp.ClientSession() as session:
        # Step 1: Call the show_welcome tool
        print("=" * 60)
        print("Step 1: Calling show_welcome tool")
        print("=" * 60)
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "show_welcome",
                "arguments": {}
            }
        }
        
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        
        async with session.post(
            "http://localhost:8000/mcp",
            json=payload,
            headers=headers
        ) as resp:
            result = await resp.json()
            print("Tool call response:")
            print(json.dumps(result, indent=2, default=str))
            
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"][0]
                if hasattr(content, "get"):
                    resource = content.get("resource")
                elif isinstance(content, dict):
                    resource = content.get("resource")
                else:
                    resource = getattr(content, "resource", None)
                
                if resource:
                    print("\nResource returned by tool:")
                    print(json.dumps(resource, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(test())
