from fastapi import APIRouter, HTTPException, Header, UploadFile, File
from pydantic import BaseModel
from openai import OpenAI
from app.core.config import settings
from app.core.security import tokeni_coz
from app.services.cv_service import cv_metni_cikart, cv_yukle, cv_ara, cv_baglan_olustur

router = APIRouter(prefix="/cv", tags=["CV İnceleme"])

llm = OpenAI(base_url=settings.lm_studio_url, api_key="lm-studio")

MAX_DOSYA_BOYUTU = 5 * 1024 * 1024  # 5 MB
IZIN_VERILEN_UZANTILAR = {".pdf", ".docx"}


def ik_yetkisi_kontrol(authorization: str) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token gerekli.")
    try:
        token_verisi = tokeni_coz(authorization.split(" ", 1)[1])
    except Exception:
        raise HTTPException(status_code=401, detail="Geçersiz token.")
    if token_verisi.get("rol") != "ik":
        raise HTTPException(status_code=403, detail="Bu işlem için İK yetkisi gerekiyor.")
    return token_verisi


class AramaIstegi(BaseModel):
    soru: str


@router.post("/yukle")
async def cv_yukle_endpoint(
    dosya: UploadFile = File(...),
    authorization: str = Header(None),
):
    token_verisi = ik_yetkisi_kontrol(authorization)
    yukleyen_id = token_verisi.get("sub", "bilinmeyen")

    uzanti = ""
    if dosya.filename:
        for ext in IZIN_VERILEN_UZANTILAR:
            if dosya.filename.lower().endswith(ext):
                uzanti = ext
                break
    if not uzanti:
        raise HTTPException(status_code=400, detail="Sadece PDF veya DOCX dosyası yüklenebilir.")

    icerik = await dosya.read()
    if len(icerik) > MAX_DOSYA_BOYUTU:
        raise HTTPException(status_code=400, detail="Dosya boyutu 5 MB'ı aşamaz.")

    try:
        metin = cv_metni_cikart(dosya.filename, icerik)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not metin.strip():
        raise HTTPException(status_code=400, detail="Dosyadan metin çıkarılamadı.")

    try:
        parca_sayisi = cv_yukle(dosya.filename, metin, yukleyen_id)
    except Exception:
        raise HTTPException(status_code=503, detail="Vektör veritabanına bağlanılamadı. Qdrant çalışıyor mu?")
    return {
        "durum": "basarili",
        "dosya": dosya.filename,
        "parca_sayisi": parca_sayisi,
        "mesaj": f"CV başarıyla yüklendi ({parca_sayisi} parça oluşturuldu).",
    }


@router.post("/ozet")
async def cv_ozet_endpoint(
    dosya: UploadFile = File(...),
    authorization: str = Header(None),
):
    ik_yetkisi_kontrol(authorization)

    uzanti = ""
    if dosya.filename:
        for ext in IZIN_VERILEN_UZANTILAR:
            if dosya.filename.lower().endswith(ext):
                uzanti = ext
                break
    if not uzanti:
        raise HTTPException(status_code=400, detail="Sadece PDF veya DOCX dosyası yüklenebilir.")

    icerik = await dosya.read()
    if len(icerik) > MAX_DOSYA_BOYUTU:
        raise HTTPException(status_code=400, detail="Dosya boyutu 5 MB'ı aşamaz.")

    try:
        metin = cv_metni_cikart(dosya.filename, icerik)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not metin.strip():
        raise HTTPException(status_code=400, detail="Dosyadan metin çıkarılamadı.")

    # Güvenli token bütçesi: prompt ~50 + CV ~300 + çıktı ~150 = ~500 token
    metin_kisalt = metin[:400]

    yanit = llm.chat.completions.create(
        model=settings.model_name,
        messages=[
            {
                "role": "user",
                "content": f"CV özeti (Türkçe, kısa):\n1. Ad/Pozisyon\n2. Deneyim\n3. 3 beceri\n\nCV:\n{metin_kisalt}",
            }
        ],
        temperature=0.2,
        max_tokens=150,
    )

    ozet = yanit.choices[0].message.content
    return {"dosya": dosya.filename, "ozet": ozet}


@router.post("/ara")
async def cv_ara_endpoint(
    istek: AramaIstegi,
    authorization: str = Header(None),
):
    ik_yetkisi_kontrol(authorization)

    if not istek.soru.strip():
        raise HTTPException(status_code=400, detail="Arama sorgusu boş olamaz.")

    sonuclar = cv_ara(istek.soru, limit=5)
    baglan = cv_baglan_olustur(sonuclar)

    yanit = llm.chat.completions.create(
        model=settings.model_name,
        messages=[
            {
                "role": "user",
                "content": f"""CV havuzunda arama yapıldı. Aşağıdaki CV parçalarına göre soruyu yanıtla.
Sadece bulunan CV'lere dayanarak yanıt ver. Türkçe yaz.

CV PARÇALARI:
{baglan}

SORU: {istek.soru}""",
            }
        ],
        temperature=0.2,
    )

    cevap = yanit.choices[0].message.content
    kaynaklar = list({s["kaynak"] for s in sonuclar})
    return {"cevap": cevap, "eslesen_cvler": kaynaklar, "sonuclar": sonuclar}
