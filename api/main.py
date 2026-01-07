from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
import time
from api.ui import router as ui_router

app = FastAPI(
    title="ForenScope API",
    description="Professional Hybrid Digital Forensics Platform API",
    version="1.0.0"
)

# In-memory job store for demonstration
JOBS = {}

app.include_router(ui_router)

class ScanRequest(BaseModel):
    target_path: str
    workers: int = 4
    enable_yara: bool = True

class CarveRequest(BaseModel):
    image_path: str
    output_dir: str
    block_size: int = 4096

class HashRequest(BaseModel):
    file_path: str
    algorithms: List[str] = ["sha256", "md5"]

class JobResponse(BaseModel):
    job_id: str
    status: str
    created_at: float

@app.get("/")
async def root():
    return {
        "status": "online",
        "engine": "ForenScope Go Engine",
        "orchestrator": "ForenScope Python Orchestrator"
    }

@app.post("/scan", response_model=JobResponse)
async def trigger_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "processing", "type": "scan", "request": request}
    # background_tasks.add_task(orchestrator.run_scan, request)
    return JobResponse(job_id=job_id, status="accepted", created_at=time.time())

@app.post("/carve", response_model=JobResponse)
async def trigger_carve(request: CarveRequest):
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "queued", "type": "carve", "request": request}
    return JobResponse(job_id=job_id, status="accepted", created_at=time.time())

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return JOBS[job_id]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}
