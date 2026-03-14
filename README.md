# Cortex HR — Şirket İçi Yapay Zeka Asistanı

Çalışanların izin sorgulayabildiği, yöneticilerin ekip bilgilerine erişebildiği,
İK'nın CV inceleme yapabildiği şirket içi bir yapay zeka asistanı.
Tüm veriler şirket sunucusunda kalır — dışarıya çıkmaz.

---

## Hedefler

- Çalışan: "Kaç gün iznim kaldı?" → anında yanıt
- Yönetici: Ekibinin izin takvimini görebilir
- İK: CV havuzunu sorgulayabilir, aday karşılaştırması yapabilir
- Herkes: Şirket politikalarını ve hiyerarşiyi sorgulayabilir

---

## Mimari

```
Kullanıcı → Next.js Arayüzü → FastAPI → Güvenlik Katmanı → Mistral (lokal) → Yanıt
                                              ↓
                                        Qdrant (bellek)
```

- **LLM:** Mistral 7B — LM Studio üzerinden lokal çalışır, internet gerekmez
- **RAG:** Qdrant vektör veritabanı — İK belgeleri, politikalar buraya yüklenir
- **Auth:** JWT token — her kullanıcı kendi yetkisi kadar görür
- **Güvenlik:** 3 katmanlı guardrail sistemi (OWASP AI Top 10)

---

## Güvenlik Katmanları

| Katman | Görev |
|--------|-------|
| Katman 1 — Giriş Denetimi | Prompt injection, hassas veri sorgusu, rol yapma, sahte yetki tespiti |
| Katman 2 — Uzunluk Denetimi | Aşırı uzun input/output engelleme (DoS koruması) |
| Katman 3 — Çıkış Denetimi | PII sızıntısı, ters metin, akrostiş, aşırı boşluk tespiti |
| Ban Sistemi | Tekrarlı ihlalde otomatik erişim askıya alma |

---

## Geliştirme Planı

| Aşama | Konu | Durum |
|-------|------|-------|
| 1 | Ortam kurulumu | ✅ Tamamlandı |
| 2 | GitHub + klasör yapısı | ✅ Tamamlandı |
| 3 | İlk FastAPI sunucusu | ✅ Tamamlandı |
| 4 | Kullanıcı girişi + JWT | ✅ Tamamlandı |
| 5 | Mistral bağlantısı | ✅ Tamamlandı |
| 6 | RAG + Qdrant | ✅ Tamamlandı |
| 7 | Güvenlik katmanları | ✅ Tamamlandı |
| 8 | Next.js arayüzü | ✅ Tamamlandı |
| 9 | Gerçek HR belgeleri | ⏳ Bekliyor |
| 10 | PostgreSQL entegrasyonu | ⏳ Bekliyor |
| 11 | SSO / Active Directory | ⏳ Bekliyor |

---

## Kurulum

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python belge_yukle.py
uvicorn app.main:app --reload --host 0.0.0.0
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Gereksinimler
- Python 3.11+
- Node.js 18+
- Docker Desktop (Qdrant için)
- LM Studio + Mistral 7B modeli

---

## Test Kullanıcıları

| Kullanıcı | Şifre | Rol |
|-----------|-------|-----|
| ahmet | test1234 | Çalışan |
| fatma | test1234 | Yönetici |
| ik | test1234 | İK |

---

## Teknoloji

- **Backend:** Python 3.11 + FastAPI
- **Frontend:** Next.js 15 + Tailwind CSS
- **LLM:** Mistral 7B (LM Studio)
- **Vektör DB:** Qdrant
- **Auth:** JWT + bcrypt
- **Güvenlik:** 3 katmanlı guardrail + ban sistemi
