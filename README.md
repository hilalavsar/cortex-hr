# Cortex HR

Şirket içi çalışan asistanı. Tüm veriler şirket altyapısında kalır.

## Genel Bakış

Cortex HR, çalışanların İK süreçlerine hızlı erişimini sağlayan, şirket belgelerine dayalı yanıtlar üreten bir yapay zeka asistanıdır. Harici bir API kullanmaz — tüm model ve veri işleme şirket sunucusunda gerçekleşir.

**Kullanım alanları**
- Yıllık izin, hastalık izni, doğum izni sorgulama
- Şirket politikaları ve el kitabı araması
- Organizasyon şeması ve raporlama hiyerarşisi
- İK süreçleri hakkında bilgi alma

## Mimari
```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Next.js    │────▶│   FastAPI    │────▶│  Güvenlik       │
│  Arayüzü   │     │   Backend    │     │  Katmanları (3) │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                   │
                              ┌────────────────────┼────────────────────┐
                              ▼                    ▼                    ▼
                       ┌─────────────┐    ┌──────────────┐    ┌──────────────┐
                       │   Qdrant    │    │   Mistral    │    │  JWT Auth    │
                       │ Vektör DB   │    │   7B (Lokal) │    │  + RBAC      │
                       └─────────────┘    └──────────────┘    └──────────────┘
```

| Bileşen | Teknoloji | Görev |
|---------|-----------|-------|
| Arayüz | Next.js 15 + Tailwind CSS | Kullanıcı chat ekranı |
| Backend | Python 3.11 + FastAPI | API, iş mantığı |
| LLM | Mistral 7B (LM Studio) | Yanıt üretimi |
| Vektör DB | Qdrant | Belge araması (RAG) |
| Auth | JWT + bcrypt | Kimlik doğrulama |
| Güvenlik | Özel guardrail sistemi | OWASP AI Top 10 |

## Güvenlik Mimarisi

Sistem, gelen her isteği üç bağımsız katmandan geçirir.

**Katman 1 — Giriş Denetimi**
Prompt injection, hassas veri sorgusu, rol yapma ve sahte yetki iddialarını regex tabanlı örüntü eşleştirme ile tespit eder.

**Katman 2 — Uzunluk Denetimi**
Input ve output uzunluklarını bağımsız olarak denetler. Aşırı uzun istekleri servis dışı bırakma (DoS) girişimi olarak değerlendirir.

**Katman 3 — Çıkış Denetimi**
LLM çıktısında TC kimlik numarası, telefon, maaş bilgisi gibi kişisel veri sızıntılarını; ters metin, akrostiş ve boşluk manipülasyonunu tespit eder.

**Ban Sistemi**
Aynı kullanıcıdan tekrarlı ihlal geldiğinde otomatik olarak erişim askıya alınır.

## Kurulum

### Gereksinimler

- Python 3.11+
- Node.js 18+
- Docker Desktop
- LM Studio (Mistral 7B modeli yüklü)

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate           # Windows
pip install -r requirements.txt
python belge_yukle.py           # HR belgelerini Qdrant'a yükle
uvicorn app.main:app --reload --host 0.0.0.0
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Qdrant (Docker)
```bash
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant
# Sonraki çalıştırmalarda:
docker start qdrant
```

## Sistem Başlatma Sırası

Her oturumda şu sıra izlenmelidir:

1. Docker Desktop'ı aç
2. `docker start qdrant`
3. LM Studio → Local Server → Start Server
4. `uvicorn app.main:app --reload --host 0.0.0.0`
5. `npm run dev`

## Proje Yapısı
```
cortex-hr/
├── backend/
│   ├── app/
│   │   ├── api/            # Endpoint'ler (auth, chat)
│   │   ├── core/           # Konfigürasyon, güvenlik
│   │   ├── services/       # RAG servisi
│   │   └── security/       # Guardrail katmanları
│   ├── tests/              # Birim ve güvenlik testleri
│   └── belge_yukle.py      # Belge yükleme scripti
├── frontend/
│   └── app/
│       └── page.tsx        # Chat arayüzü
├── data/
│   └── hr_docs/            # Şirket belgeleri (.md)
└── docs/
    ├── architecture/       # Mimari kararlar (ADR)
    └── security/           # OWASP değerlendirmesi
```

## Geliştirme Durumu

| Aşama | Konu | Durum |
|-------|------|-------|
| 1 | Ortam kurulumu | ✅ |
| 2 | GitHub + proje iskeleti | ✅ |
| 3 | FastAPI sunucusu | ✅ |
| 4 | JWT kimlik doğrulama | ✅ |
| 5 | Mistral bağlantısı | ✅ |
| 6 | RAG + Qdrant entegrasyonu | ✅ |
| 7 | Güvenlik katmanları | ✅ |
| 8 | Next.js arayüzü | ✅ |
| 9 | Gerçek HR belgeleri | ⏳ |
| 10 | PostgreSQL entegrasyonu | ⏳ |
| 11 | SSO / Active Directory | ⏳ |

## Test Kullanıcıları

Geliştirme ortamı için örnek kullanıcılar:

| Kullanıcı Adı | Şifre | Rol |
|---------------|-------|-----|
| ahmet | test1234 | Çalışan |
| fatma | test1234 | Yönetici |
| ik | test1234 | İK |

> **Not:** Üretim ortamına geçişte bu kullanıcılar kaldırılmalı, gerçek kimlik doğrulama sistemi (SSO / Active Directory) entegre edilmelidir.
