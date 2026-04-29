"""
Hermes Voice Wrapper — FastAPI bridge between Home Assistant and Hermes Agent.

Calls the `hermes` CLI via subprocess. The hermes binary is mounted from the host.
"""
import asyncio
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Hermes Voice Wrapper")
logger = logging.getLogger("hermes_wrapper")

HERMES_TIMEOUT = 55


class VoiceRequest(BaseModel):
    text: str
    conversation_id: str = ""
    language: str = "fr"
    device_id: str | None = None


class VoiceResponse(BaseModel):
    speech: str
    conversation_id: str = ""


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/voice", response_model=VoiceResponse)
async def voice(req: VoiceRequest):
    """Forward text to Hermes Agent CLI and return the response."""
    cmd = ["/usr/local/bin/hermes", "run", "--message", req.text]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=HERMES_TIMEOUT
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Hermes timed out")
    except FileNotFoundError:
        raise HTTPException(
            status_code=500, detail="Hermes binary not found at /usr/local/bin/hermes"
        )

    if proc.returncode != 0:
        logger.error("Hermes failed (rc=%d): %s", proc.returncode, stderr.decode())
        raise HTTPException(status_code=502, detail="Hermes returned an error")

    response_text = stdout.decode().strip()
    if not response_text:
        response_text = "Je n'ai pas de reponse."

    return VoiceResponse(
        speech=response_text,
        conversation_id=req.conversation_id,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
