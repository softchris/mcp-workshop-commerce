@app.post("/ask")
async def ask_question(request: QuestionRequest):
    question = request.question

    res = await run("get_faq_answer", {"query": question})
    content = res.content[0].text if res.content else "No content"
    
    return {"answer": content}