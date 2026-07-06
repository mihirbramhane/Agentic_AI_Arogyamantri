"""Translate the final guidance into the user's language.

Returns plain text; the Next.js frontend speaks it aloud with the Web Speech API
(SpeechSynthesis), reusing your existing multilingual + voice work.
"""
from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from crewai import LLM

from app.config import get_settings

_LANG_NAMES = {
    "en": "English", "hi": "Hindi", "te": "Telugu",
    "ta": "Tamil", "bn": "Bengali", "mr": "Marathi",
}


class TranslateInput(BaseModel):
    text: str = Field(..., description="English guidance to translate")
    language: str = Field("en", description="Target language ISO code")


class TranslateTool(BaseTool):
    name: str = "translator"
    description: str = (
        "Translate the final, plain-language guidance into the user's language so "
        "it can be read aloud. Keeps it simple and reassuring for low-literacy users."
    )
    args_schema: Type[BaseModel] = TranslateInput

    def _run(self, text: str, language: str = "en") -> str:
        if language == "en":
            return text
        s = get_settings()
        target = _LANG_NAMES.get(language, language)
        llm = LLM(model=s.llm_model, api_key=s.openai_api_key)
        prompt = (
            f"Translate the following guidance into simple, spoken {target} that a "
            f"person with limited literacy can understand. Keep it warm and clear. "
            f"Return only the translation:\n\n{text}"
        )
        return llm.call(prompt)
