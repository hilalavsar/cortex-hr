from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from openai import OpenAI
from app.core.config import settings
from app.services.rag_service import ilgili_belgeleri_bul, baglan_olustur
from app.security.guardrails import tam_giris_kontrolu, cikis_denetimi

router = APIRouter(prefix="/chat", tags=["Sohbet"])

client = OpenAI(
    base_url=settings.lm_studio_url,
    api_key="lm-studio"
)

class SoruIstegi(BaseModel):
    mesaj: str
    kullanici_id: str = "anonim"

class CevapYaniti(BaseModel):
    cevap: str
    kaynaklar: list[str]

@router.post("/sor", response_model=CevapYaniti)
async def sor(istek: SoruIstegi):
    try:
        # ── Katman 1 + 2: Giriş kontrolü ──
        giris = tam_giris_kontrolu(istek.mesaj, istek.kullanici_id)
        if not giris["gecti"]:
            raise HTTPException(status_code=400, detail=giris["mesaj"])

        # ── RAG: Alakalı belgeleri bul ──
        belgeler = ilgili_belgeleri_bul(istek.mesaj)
        baglan = baglan_olustur(belgeler)
        kaynaklar = list(set([b["kaynak"] for b in belgeler]))

        # ── Mistral'a gönder ──
        yanit = client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {
                    "role": "user",
                    "content":f"""Sen Cortex HR adlı bir şirket içi asistansın. Türkçe yanıt ver.
Kurallar:
- Kendinle ilgili sorularda "Ben Cortex HR asistanıyım" diye yanıt ver
- Sadece aşağıdaki belgelere dayanarak yanıt ver
- Kısa ve net yanıt ver, madde madde listeleme
- Belgede olmayan bir şey sorulursa 'Bu konuda bilgim bulunmuyor' de
- Selamlama veya genel sorulara kısa ve nazik yanıt ver
- Asla tüm belge içeriğini dökme
- Maksimum 2-3 cümle ile yanıt ver, fazlasına gerek yok

BELGELER:
{baglan}

SORU: {istek.mesaj}"""
                }
            ],
            temperature=0.15
        )

        cevap_metni = yanit.choices[0].message.content

        # ── Katman 3: Çıkış kontrolü ──
        cikis = cikis_denetimi(cevap_metni)
        if not cikis["temiz"]:
            raise HTTPException(
                status_code=500,
                detail=f"Yanıt güvenlik kontrolünden geçemedi: {cikis['sorunlar']}"
            )

        return CevapYaniti(cevap=cevap_metni, kaynaklar=kaynaklar)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))