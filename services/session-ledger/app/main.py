from fastapi import FastAPI, HTTPException, status
from app.schemas import SessionLedgerRequest, SessionSummaryOutput
from app.chain import run_session_ledger

app = FastAPI(
    title="TTRPG Session Ledger Service",
    description="Microservice responsible for parsing, structuring, and cataloging session notes.",
    version="1.0.0"
)

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Basic health check route for monitoring microservice status."""
    return {"status": "healthy", "service": "session-ledger"}

@app.post(
    "/api/v1/session/summarize",
    response_model=SessionSummaryOutput,
    status_code=status.HTTP_200_OK
)
async def summarize_session_endpoint(payload: SessionLedgerRequest):
    """Parses unorganized session notes into structured recaps and extracted entities."""
    try:
        summary_result = run_session_ledger(payload)
        return summary_result
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing AI chain: {str(error)}"
        )