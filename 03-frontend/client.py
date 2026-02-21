from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
import asyncio
import json
from typing import Optional, Dict, Any, List
from mcp.shared.context import RequestContext
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream

from llm import call_llm
from typing import AsyncGenerator

import mcp.types as types

from mcp.types import (
    CallToolResult,
    LoggingMessageNotificationParams,
    TextContent,
)

from mcp.shared.session import RequestResponder

class LoggingCollector:
    def __init__(self):
        self.log_messages: list[LoggingMessageNotificationParams] = []

    async def __call__(self, params: LoggingMessageNotificationParams) -> None:
        self.log_messages.append(params)

logging_collector = LoggingCollector()

port = 8000

async def handle_sampling_message(
    context: RequestContext[ClientSession, None], params: types.CreateMessageRequestParams
) -> types.CreateMessageResult:
    # print(f"Sampling request: {params.messages}")

    message = params.messages[0].content.text

    # todo, call an actual llm and change below
    response = await call_llm(message)

    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text=response,
        ),
        model="gpt-3.5-turbo",
        stopReason="endTurn",
    )

# I get normal messages, notifications, and exceptions
async def message_handler(
        message: RequestResponder[types.ServerRequest, types.ClientResult]
        | types.ServerNotification
        | Exception,
    ) -> None:
        print("Received message:", message)
        if isinstance(message, Exception):
            raise message
        else:
            if isinstance(message, types.ServerNotification):
                print("NOTIFICATION:", message)
            elif isinstance(message, RequestResponder):
                print("REQUEST_RESPONDER:", message)
            else:
                print("SERVER_REQUEST:", message)

async def main(tool_name: str, params) -> CallToolResult:
    print("Starting client...")
    # Connect to a streamable HTTP server
    async with streamablehttp_client(f"http://localhost:{port}/mcp") as (
        read_stream,
        write_stream,
        session_callback,
    ): 
        # Create a session using the client streams
        async with ClientSession(
            read_stream, 
            write_stream,
            logging_callback=logging_collector,
            message_handler=message_handler,
            sampling_callback=handle_sampling_message
        ) as session:

            # Initialize the connection
            await session.initialize()

            # id = session_callback()
            # print("ID: ", id)

            print("Session initialized, ready to call tools.")
          
            # Call a tool
            results = []
            tool_result = await session.call_tool(tool_name, params)

            print("Tool result:", tool_result)
            return tool_result

async def run(tool_name: str, params):
    return await main(tool_name, params)

if __name__ == "__main__":
    asyncio.run(main("echo", {"message": "hello"}))
            
