from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from app.core.config import settings
from app.services.rag_service import ilgili_belgeleri_bul, baglan_olustur

router = APIRouter(prefix="/chat", tags=["Sohbet"])

client = OpenAI(
    base_url=settings.lm_studio_url,
    api_key="lm-studio"
)

class SoruIstegi(BaseModel):
    mesaj: str

class CevapYaniti(BaseModel):
    cevap: str
    kaynaklar: list[str]

@router.post("/sor", response_model=CevapYaniti)
async def sor(istek: SoruIstegi):
    try:
        # Alakalı belgeleri bul
        belgeler = ilgili_belgeleri_bul(istek.mesaj)
        baglan = baglan_olustur(belgeler)
        kaynaklar = list(set([b["kaynak"] for b in belgeler]))

        # Mistral'a gönder
        yanit = client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {
                    "role": "user",
                    "content": f"""Sen Cortex HR adlı bir şirket içi asistansın. 
Türkçe yanıt ver. Sadece aşağıdaki belgelere dayanarak yanıt ver.
Belgede olmayan bir şey sorulursa 'Bu konuda bilgim bulunmuyor' de.

BELGELER:
{baglan}

SORU: {istek.mesaj}"""
                }
            ],
            temperature=0.3
        )
        return CevapYaniti(
            cevap=yanit.choices[0].message.content,
            kaynaklar=kaynaklar
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))