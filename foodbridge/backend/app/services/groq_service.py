"""Wrapper around Google's Gemini API with defensive JSON handling.

Three layers of safety against malformed model output:
 1. Gemini JSON mode via response_mime_type="application/json"
 2. json.loads with one retry pass if it fails
 3. Pydantic schema validation before the result enters LangGraph state
"""
import json
from pydantic import BaseModel, ValidationError
import google.generativeai as genai
from app.config import settings, get_logger

logger = get_logger(__name__)

_client = None


def get_client():
    global _client
    if _client is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _client = genai.GenerativeModel(settings.GEMINI_MODEL)
    return _client


class AIDecision(BaseModel):
    accepted: bool
    selectedNGO: str
    reason: str
    emailSubject: str
    emailBody: str


def _try_parse(raw: str) -> dict | None:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Strip common wrapping issues (markdown fences, stray text) and retry once
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json\n", "", 1)
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            cleaned = cleaned[start : end + 1]
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None


def call_gemini_json(system_prompt: str, user_prompt: str) -> AIDecision:
    """Calls Gemini, forces JSON mode, validates, and falls back to a safe
    rejection decision if parsing/validation ultimately fails.
    """
    client = get_client()

    try:
        prompt = f"{system_prompt}\n\nUser request:\n{user_prompt}"
        response = client.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 1000,
                "response_mime_type": "application/json",
            },
        )
        raw = getattr(response, "text", "") or ""
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        return AIDecision(
            accepted=False,
            selectedNGO="",
            reason="AI service unavailable, donation could not be evaluated.",
            emailSubject="",
            emailBody="",
        )

    data = _try_parse(raw)
    if data is None:
        logger.error(f"Gemini returned unparsable JSON: {raw[:300]}")
        return AIDecision(
            accepted=False,
            selectedNGO="",
            reason="AI response was not valid JSON. Donation rejected for safety.",
            emailSubject="",
            emailBody="",
        )

    try:
        return AIDecision(**data)
    except ValidationError as e:
        logger.error(f"Gemini JSON failed schema validation: {e} | raw={data}")
        return AIDecision(
            accepted=False,
            selectedNGO="",
            reason="AI response did not match expected schema. Donation rejected for safety.",
            emailSubject="",
            emailBody="",
        )


def call_groq_json(system_prompt: str, user_prompt: str) -> AIDecision:
    return call_gemini_json(system_prompt, user_prompt)
