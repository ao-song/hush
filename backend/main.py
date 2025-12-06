import secrets
import time

from fastapi import FastAPI, HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel


# Create a limiter instance that uses the client's IP address
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In-memory store for secrets
# { "unique_id": {"secret": "your_secret", "timestamp": creation_time, "viewed": False} }
secrets_store = {}

class SecretCreate(BaseModel):
    secret: str

@app.post("/api/create_secret/")
@limiter.limit("60/minute")
async def create_secret(_request: Request, secret_data: SecretCreate):
    unique_id = secrets.token_urlsafe(16)
    secrets_store[unique_id] = {
        "secret": secret_data.secret,
        "timestamp": time.time(),
        "viewed": False
    }
    return {"link": f"/secret/{unique_id}"}

@app.get("/api/secret/{unique_id}")
@limiter.limit("60/minute")
async def get_secret(_request: Request, unique_id: str):
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
