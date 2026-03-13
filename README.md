# Cortex HR — Şirket İçi Yapay Zeka Asistanı

Çalışanların izin sorgulayabildiği, yöneticilerin ekip bilgilerine erişebildiği,
İK'nın CV inceleme yapabildiği şirket içi bir yapay zeka asistanı.
Tüm veriler şirket sunucusunda kalır — dışarıya çıkmaz.

---

## Hedefler

- Çalışan: "Kaç gün iznim kaldı?" → anında yanıt
- Yönetici: Ekibinin izin takvimini görebilir
- İK: CV havuzunu sorgulayabilir, aday karşılaştırması yapabilir
- Herkes: Şirket politikalarını, hiyerarşiyi sorgulayabilir

---

## Mimari
```
Kullanıcı → FastAPI → Güvenlik Katmanı → Mistral (lokal) → Yanıt
                           ↓
                      Qdrant (bellek)
```

- **LLM:** Mistral 7B — şirket bilgisayarında çalışır, internet gerekmez
- **RAG:** Qdrant vektör veritabanı — İK belgeleri, politikalar buraya yüklenir
- **Auth:** JWT token — her kullanıcı kendi yetkisi kadar görür
- **Güvenlik:** OWASP AI Top 10 testleri ile doğrulanmış

---

## Geliştirme Planı

| Aşama | Konu | Durum |
|-------|------|-------|
| 1 | Ortam kurulumu | ✅ Tamamlandı |
| 2 | GitHub + klasör yapısı | ✅ Tamamlandı |
| 3 | İlk FastAPI sunucusu | ✅ Tamamlandı |
| 4 | Kullanıcı girişi + JWT | 🔄 Devam ediyor |
| 5 | Mistral bağlantısı | ⏳ Bekliyor |
| 6 | RAG + Qdrant | ⏳ Bekliyor |
| 7 | Güvenlik testleri | ⏳ Bekliyor |

---

## Kurulum
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Teknoloji

- **Backend:** Python + FastAPI
- **LLM:** Mistral 7B (LM Studio)
- **Vektör DB:** Qdrant
- **Auth:** JWT
```
