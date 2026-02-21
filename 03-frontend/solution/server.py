# change so it calls the LLM faq instead

# new FAQ tool that uses LLM sampling context to provide better answers
@mcp.tool(description="Get a better FAQ answer from the LLM by providing it with the entire FAQ context")
async def get_faq_answer(query: str, ctx: Context[ServerSession, None]) -> str:
    """Get a better FAQ answer from the LLM by providing it with the entire FAQ context"""

    faq_str = ""
    for question, answer in faq.items():
        faq_str += f"Q: {question}\nA: {answer}\n\n"

    prompt = f"Using the following FAQ context, {faq_str} and determine the best answer to the following question: {query}"

    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user",
                content=TextContent(type="text", text=prompt),
            )
        ],
        max_tokens=100,
    )

    faq_response = result.content.text

    return faq_response
