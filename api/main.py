from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

app = FastAPI(
    title="ForenScope API",
    description="REST API for the ForenScope Digital Forensics Platform",
    version="0.1.0"
)

class ScanRequest(BaseModel):
    image_path: str
    scan_type: str = "full"
    
class JobStatus(BaseModel):
    job_id: str
    status: str
    result: dict | None = None

@app.get("/")
async def root():
    return {"message": "ForenScope API is running"}

@app.post("/scan", response_model=JobStatus)
async def trigger_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """
    Trigger a new forensic scan task.
    """
    job_id = "job_12345" # Mock ID
    # In real imp: orchestrator.submit_job(...)
    return JobStatus(job_id=job_id, status="queued")

@app.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get the status of a specific job.
    """
    return JobStatus(job_id=job_id, status="running")
