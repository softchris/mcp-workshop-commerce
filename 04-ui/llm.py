# to call GitHub Models or GitHub Copilot SDK
# take a prompt and return a response

import asyncio
from copilot import CopilotClient


async def call_llm(query: str) -> str:
    client = CopilotClient()
    await client.start()

    session = await client.create_session({"model": "gpt-4.1"})
    response = await session.send_and_wait({
        "prompt": query}
    )
    result = response.data.content
    # print(result)
    await client.stop()

    return result


if __name__ == "__main__":
    asyncio.run(call_llm("What is 2 + 2?"))