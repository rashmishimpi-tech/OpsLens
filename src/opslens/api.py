from fastapi import APIRouter, HTTPException, status
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from opslens.agent.graph import build_graph
from opslens.database import check_database_connection

router = APIRouter()

agent_graph = build_graph()

class AgentQueryRequests(BaseModel):
    question: str  = Field(min_length=1)

class AgentQueryResponse(BaseModel):
    answer: str

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness() -> dict[str, str]:
    try:
        check_database_connection()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        ) from exc

    return {"status": "ready"}

@router.post(
    "/agent/query",
    response_model=AgentQueryResponse,
    status_code=status.HTTP_200_OK,
)
async def query_agent(
    request: AgentQueryRequests,
) -> AgentQueryResponse:
    result = agent_graph.invoke(
        {
            "messages" : [
                HumanMessage(content=request.question)
            ],
            "sql_retries": 0,
        }
    )

    messages = result["messages"]

    if not messages:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent return no response"
        )

    final_message = messages[-1]

    if not isinstance(final_message, AIMessage):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent returned invalid resposne"
        )

    return AgentQueryResponse(
        answer = str(final_message.content)
    )