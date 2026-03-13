from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def sifreyi_hashle(sifre: str) -> str:
    return pwd_context.hash(sifre)

def sifre_dogru_mu(sifre: str, hashli_sifre: str) -> bool:
    return pwd_context.verify(sifre, hashli_sifre)

def token_olustur(data: dict) -> str:
    kopyala = data.copy()
    bitis = datetime.now(timezone.utc) + timedelta(minutes=settings.token_expire_minutes)
    kopyala.update({"exp": bitis})
    return jwt.encode(kopyala, settings.secret_key, algorithm=settings.algorithm)

def tokeni_coz(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])