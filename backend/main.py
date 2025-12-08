import secrets
import time
import os

from fastapi import FastAPI, HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel

# Get the subpath from environment variable, default to an empty string.
APP_SUB_PATH = os.getenv("APP_SUB_PATH", "")
# Normalize APP_SUB_PATH.
# It should be a path starting and ending with a slash, e.g., /subpath/
# or just "/" if no subpath is defined.
if APP_SUB_PATH and APP_SUB_PATH != "/":
    APP_SUB_PATH = f"/{APP_SUB_PATH.strip('/')}/"
else:
    APP_SUB_PATH = "/"

# Create a limiter instance that uses the client's IP address
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter

# Wrapper to satisfy FastAPI's expected exception handler signature (accepts Exception)
async def _rate_limit_handler(request: Request, exc: Exception):
    if isinstance(exc, RateLimitExceeded):
        return _rate_limit_exceeded_handler(request, exc)
    raise exc

app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

# In-memory store for secrets
# { "unique_id": {"secret": "your_secret", "timestamp": creation_time, "viewed": False} }
secrets_store = {}

class SecretCreate(BaseModel):
    secret: str

@app.post("/api/create_secret/")
@limiter.limit("60/minute")
async def create_secret(request: Request, secret_data: SecretCreate):
    unique_id = secrets.token_urlsafe(16)
    secrets_store[unique_id] = {
        "secret": secret_data.secret,
        "timestamp": time.time(),
        "viewed": False
    }
    return {"link": f"{APP_SUB_PATH}secret/{unique_id}"}

@app.get("/api/secret/{unique_id}")
@limiter.limit("60/minute")
async def get_secret(request: Request, unique_id: str):
    secret_entry = secrets_store.get(unique_id)

    if not secret_entry:
        raise HTTPException(status_code=404, detail="Secret not found or already expired/viewed.")

    # Check for expiration (1 minute)
    if time.time() - secret_entry["timestamp"] > 60:
        del secrets_store[unique_id]
        raise HTTPException(status_code=404, detail="Secret expired.")

    # Check if already viewed
    if secret_entry["viewed"]:
        del secrets_store[unique_id]
        raise HTTPException(status_code=404, detail="Secret already viewed.")

    secret_entry["viewed"] = True
    secret_content = secret_entry["secret"]
    del secrets_store[unique_id]

    return {"secret": secret_content}
