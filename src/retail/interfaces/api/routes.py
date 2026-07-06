"""
REST API routes for the retail AI agent.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from retail.agent.core import RetailAgent

app = FastAPI(title="Retail AI Agent API", version="0.1.0")

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    question: str
    sql: str
    answer: str

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a natural language question about the retail data."""
    try:
        agent = RetailAgent()
        answer = agent.ask(request.question)
        
        # Get the SQL query (we need to modify the agent to return it)
        # For now, we'll just return the answer
        return QuestionResponse(
            question=request.question,
            sql="",  # TODO: Return the actual SQL
            answer=answer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}