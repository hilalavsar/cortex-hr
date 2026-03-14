from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.core.security import sifreyi_hashle, sifre_dogru_mu, token_olustur

router = APIRouter(prefix="/auth", tags=["Giriş"])

# Geçici kullanıcı listesi — ileride veritabanına taşıyacağız
KULLANICILAR = {
    "ahmet": {
        "id": "usr_001",
        "sifre": "$2b$12$fDd9YOOpbdfsHzVFmfDkaeWc1b.ukjbzBP6XeqFpWbDBVicvOf9iG",
        "rol": "calisan",
        "ad": "Ahmet Yılmaz"
    },
    "fatma": {
        "id": "usr_002",
        "sifre": "$2b$12$fDd9YOOpbdfsHzVFmfDkaeWc1b.ukjbzBP6XeqFpWbDBVicvOf9iG",
        "rol": "yonetici",
        "ad": "Fatma Kaya"
    },
    "ik": {
        "id": "usr_003",
        "sifre": "$2b$12$fDd9YOOpbdfsHzVFmfDkaeWc1b.ukjbzBP6XeqFpWbDBVicvOf9iG",
        "rol": "ik",
        "ad": "İK Yöneticisi"
    },
}

class GirisIstegi(BaseModel):
    kullanici_adi: str
    sifre: str

class TokenYaniti(BaseModel):
    token: str
    rol: str
    ad: str

@router.post("/giris", response_model=TokenYaniti)
async def giris(istek: GirisIstegi):
    kullanici = KULLANICILAR.get(istek.kullanici_adi)
    if not kullanici or not sifre_dogru_mu(istek.sifre, kullanici["sifre"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı"
        )
    token = token_olustur({
        "sub": kullanici["id"],
        "rol": kullanici["rol"],
        "ad": kullanici["ad"]
    })
    return TokenYaniti(token=token, rol=kullanici["rol"], ad=kullanici["ad"])