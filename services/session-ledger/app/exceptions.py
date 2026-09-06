from fastapi import Request, status
from fastapi.responses import JSONResponse


class LLMProcessingError(Exception):
    def __init__(self, detail: str):
        self.detail = detail

class DatabaseTransactionError(Exception):
    def __init__(self, detail: str):
        self.detail = detail

async def llm_processing_handler(request: Request, exc: LLMProcessingError):
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY, 
        content={
            "error": "AI Extraction Failed",
            "message": exc.detail,
            "path": request.url.path
        }
    )

async def database_transaction_handler(request: Request, exc: DatabaseTransactionError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database Operation Failed",
            "message": exc.detail,
            "path": request.url.path
        }
    )