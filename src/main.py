from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.models import LBWInput, LBWOutput
from src.decision_engine import process_decision

app = FastAPI(
    title="Decision Making API",
    description="API for Decision Review System (DRS)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )

@app.post("/api/lbw-decision", response_model=LBWOutput)
async def get_lbw_decision(input_data: LBWInput):
    try:
        result = process_decision(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))