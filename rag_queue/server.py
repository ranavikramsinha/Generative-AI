# flake8: noqa
from fastapi import FastAPI, Query, Path
from .queue.connection import queue
from .queue.worker import process_query

app = FastAPI()

@app.get('/')
def root():
    return {"status": 'Server is running and up'}

@app.post('/chat')
def chat(
    query: str = Query(..., description="Chat Message")
):
    #? put the Query in queue
    #? tell user, your job is received
    job = queue.enqueue(process_query, query) #? process_query function call with query parameter
    return {"status": "queued", "job_id": job.id}

@app.get("/result/{job_id}")
def get_result(
    job_id: str = Path(..., description="Job ID")
):
    job = queue.fetch_job(job_id=job_id)
    result = job.return_value()
    
    return {"result": result}  