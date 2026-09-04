from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import SessionLedgerRequest, SessionSummaryOutput, SessionResponse, SessionUpdateRequest
from app.chain import run_session_ledger_async
from app.database import get_db
from app import crud

app = FastAPI(
    title="TTRPG Session Ledger Service",
    description="Microservice responsible for parsing, structuring, and cataloging session notes.",
    version="1.0.0"
)

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy", "service": "session-ledger"}

@app.post(
    "/api/v1/session/summarize",
    response_model=SessionSummaryOutput,
    status_code=status.HTTP_200_OK
)
async def summarize_session_endpoint(
    payload: SessionLedgerRequest,
    db: AsyncSession = Depends(get_db)  # <-- Injects the async database session
):
    try:
        #Execute the LLM Pipeline
        summary_result = await run_session_ledger_async(payload)
        
        #Persist the Data
        campaign = await crud.get_or_create_campaign(
            db=db, 
            name=payload.campaign_name, 
            system=payload.game_system
        )
        
        await crud.save_session_data(
            db=db,
            campaign_id=campaign.id,
            raw_notes=payload.raw_notes,
            llm_output=summary_result
        )
        
        #Return the payload to the user
        return summary_result
        
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing AI chain or saving to DB: {str(error)}"
        )

@app.get(
    "/api/v1/session/{session_id}",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK
)
async def get_session_endpoint(
    session_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Retrieves a specific session and all its extracted entities."""
    db_session = await crud.get_session_by_id(db, session_id)
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return db_session

@app.put(
    "/api/v1/session/{session_id}",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK
)
async def update_session_endpoint(
    session_id: int, 
    payload: SessionUpdateRequest, 
    db: AsyncSession = Depends(get_db)
):
    """Updates the title or unresolved hooks of a saved session."""
    db_session = await crud.get_session_by_id(db, session_id)
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    updated_session = await crud.update_session(db, db_session, payload)
    return updated_session

@app.delete(
    "/api/v1/session/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_session_endpoint(
    session_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Deletes a session and its associated entities from the database."""
    db_session = await crud.get_session_by_id(db, session_id)
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    await crud.delete_session(db, db_session)
    # 204 No Content responses must not return a body
    return None