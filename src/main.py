import traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.models import LBWInput, LBWOutput
from src.decision_engine import process_decision

app = FastAPI(
    title="Cricket Decision Review System API",
    description="API for LBW & swing analysis using minimal input fields",
    version="2.1.0",
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
    return JSONResponse(status_code=422, content={"detail": str(exc)})

@app.exception_handler(Exception)
async def log_exceptions(request: Request, exc: Exception):
    # Print full traceback to stderr
    traceback.print_exc(file=sys.stderr)
    return JSONResponse(status_code=500, content={"detail": repr(exc)})


@app.post("/api/lbw-decision", response_model=LBWOutput)
async def get_lbw_decision(payload: LBWInput):
    try:
        return process_decision(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))