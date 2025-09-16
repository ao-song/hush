from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import secrets
import time

app = FastAPI()

# In-memory store for secrets
# { "unique_id": {"secret": "your_secret", "timestamp": creation_time, "viewed": False} }
secrets_store = {}

class SecretCreate(BaseModel):
    secret: str

@app.post("/api/create_secret/")
async def create_secret(secret_data: SecretCreate):
    unique_id = secrets.token_urlsafe(16)
    secrets_store[unique_id] = {
        "secret": secret_data.secret,
        "timestamp": time.time(),
        "viewed": False
    }
    return {"link": f"/secret/{unique_id}"}

@app.get("/api/secret/{unique_id}")
async def get_secret(unique_id: str):
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
