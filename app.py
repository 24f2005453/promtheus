from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import time
import uuid
from collections import deque

EMAIL = "24f2005453@ds.study.iitm.ac.in"

app = FastAPI()

start_time = time.time()

# Prometheus counter
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests"
)

# In-memory log buffer
logs = deque(maxlen=1000)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    http_requests_total.inc()

    request_id = str(uuid.uuid4())

    entry = {
        "level": "INFO",
        "ts": time.time(),
        "path": request.url.path,
        "request_id": request_id,
    }

    logs.append(entry)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/work")
def work(n: int = 1):
    # simulate work
    for _ in range(n):
        pass

    return {
        "email": EMAIL,
        "done": n
    }


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "uptime_s": time.time() - start_time
    }


@app.get("/logs/tail")
def tail(limit: int = 10):
    return list(logs)[-limit:]


@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest().decode(),
        media_type=CONTENT_TYPE_LATEST
    )
