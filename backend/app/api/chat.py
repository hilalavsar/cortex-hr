from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["Sohbet"])

client = OpenAI(
    base_url=settings.lm_studio_url,
    api_key="lm-studio"
)

class SoruIstegi(BaseModel):
    mesaj: str

class CevapYaniti(BaseModel):
    cevap: str

@router.post("/sor", response_model=CevapYaniti)
async def sor(istek: SoruIstegi):
    try:
        yanit = client.chat.completions.create(
            model=settings.model_name,
            messages=[
        {
            "role": "user",
            "content": f"Sen Cortex HR adlı bir şirket içi asistansın. Türkçe yanıt ver.\n\nKullanıcı sorusu: {istek.mesaj}"
        }
        ],
            temperature=0.3
        )
        return CevapYaniti(cevap=yanit.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))