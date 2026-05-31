from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
import threading
import uuid
import datetime
from worker import worker
from state import JOBS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

SERVER_START = datetime.datetime.now().isoformat()
print(f"[API] server started at {SERVER_START}", flush=True)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "server_started_at": SERVER_START,
        "job_count": len(JOBS)
    }


@app.post("/run_graph")
async def run_graph(request: Request):
    # mode:'no-cors' で送られた text/plain ボディも JSON としてパース
    body = await request.body()
    payload = json.loads(body)
    concept = payload["concept"]
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "running", "concept": concept, "started_at": datetime.datetime.now().isoformat()}
    print(f"[API] POST /run_graph concept={concept!r} job_id={job_id}", flush=True)
    threading.Thread(target=worker, args=(job_id, concept)).start()
    return {"status": "started", "job_id": job_id}


# GETエンドポイント: クエリパラメータで受け取る（CORSプリフライト不要・Web用）
@app.get("/run_graph")
def run_graph_get(concept: str):
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "running", "concept": concept, "started_at": datetime.datetime.now().isoformat()}
    print(f"[API] GET /run_graph concept={concept!r} job_id={job_id}", flush=True)
    threading.Thread(target=worker, args=(job_id, concept)).start()
    return {"status": "started", "job_id": job_id}


@app.get("/result/{job_id}")
def get_result(job_id: str):
    job = JOBS.get(job_id)
    print(f"[API] GET /result/{job_id} → {job.get('status') if job else 'not_found'}", flush=True)

    if job is None:
        return {
            "job_id": job_id,
            "data": {"status": "error", "error": "job not found (server may have restarted)"},
        }

    return {
        "job_id": job_id,
        "data": job
    }