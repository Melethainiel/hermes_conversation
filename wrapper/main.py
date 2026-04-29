"""
Hermes Voice Wrapper — FastAPI bridge between Home Assistant and Hermes Agent.

Receives POST /voice from HA ConversationEntity, calls Hermes via AIAgent library,
returns the response synchronously.
"""
import os
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from run_agent import AIAgent

app = FastAPI(title="Hermes Voice Wrapper")
logger = logging.getLogger("hermes_wrapper")

# Optional: pre-create a shared agent instance for faster responses
_agent: AIAgent | None = None


def get_agent() -> AIAgent:
    """Lazy-init a shared AIAgent instance."""
    global _agent
    if _agent is None:
        _agent = AIAgent(quiet_mode=True)
    return _agent


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
    """Forward text to Hermes Agent and return the response."""
    agent = get_agent()

    try:
        response = agent.chat(req.text)
    except Exception as ex:
        logger.exception("Hermes agent error")
        raise HTTPException(status_code=502, detail=str(ex))

    if not response:
        response = "Je n'ai pas de reponse."

    return VoiceResponse(
        speech=response,
        conversation_id=req.conversation_id,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
