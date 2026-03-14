import re
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# KATMAN 1 — GİRİŞ DENETİMİ
# ─────────────────────────────────────────────

INJECTION_KALIPLARI = [
    re.compile(r"ignore\s+(previous|all|above)\s+(instructions?|rules?)", re.I),
    re.compile(r"(önceki|tüm|bütün)\s+(talimatları|kuralları)\s+(unut|ignore)", re.I),
    re.compile(r"(pretend|act)\s+.*(no\s+restrictions?)", re.I),
    re.compile(r"\bDAN\b"),
    re.compile(r"jailbreak", re.I),
    re.compile(r"system\s*prompt\s*(göster|ver|nedir)", re.I),
    re.compile(r"(admin|root)\s*(mod|mode|yetkisi)", re.I),
]

HASSAS_KALIPLER = [
    re.compile(r"(maaş|salary)\s*(listesi|tümü|hepsi)", re.I),
    re.compile(r"tüm\s+çalışanların\s+(maaş|tc|telefon)", re.I),
    re.compile(r"(şifre|password|token)\s*(ver|göster|nedir)", re.I),
    re.compile(r"veritabanı\s*(şeması|tabloları)", re.I),
]

HIKAYE_KALIPLARI = [
    re.compile(r"(bir varmış bir yokmuş|masal|hikaye|rol yap|roleplay)", re.I),
    re.compile(r"(sanki sen|diyelim ki sen|imagine you|pretend you are)", re.I),
    re.compile(r"(karakter oyna|karakter ol|sen artık)", re.I),
    re.compile(r"(senaryo|scenario|fiction|kurgu)", re.I),
]

SAHTE_YETKI_KALIPLARI = [
    re.compile(r"ben\s+(admin|yönetici|genel müdür|ceo|sistem)", re.I),
    re.compile(r"(admin|root|superuser)\s*(olarak|modunda|yetkisiyle)", re.I),
    re.compile(r"(özel yetkim|tam yetkim|her şeye erişimim) var", re.I),
    re.compile(r"(ben|benim)\s+.*(sistem|güvenlik)\s*(yöneticisi|uzmanı)", re.I),
]


def giris_denetimi(metin: str) -> dict:
    """Katman 1 — injection, hassas veri, hikaye, sahte yetki kontrolü."""

    for kalip in INJECTION_KALIPLARI:
        if kalip.search(metin):
            return {
                "gecti": False,
                "katman": "giris_denetimi",
                "tehdit": "prompt_injection",
                "mesaj": "Bu konuda size yardımcı olamıyorum. Farklı bir soru sormak ister misiniz?"
               #"mesaj": "Güvenlik politikası ihlali tespit edildi."
            }

    for kalip in HASSAS_KALIPLER:
        if kalip.search(metin):
            return {
                "gecti": False,
                "katman": "giris_denetimi",
                "tehdit": "hassas_veri_sorgusu",
                #"mesaj": "Bu tür sorgular yetkisiz."
                "mesaj": "Bu konuda size yardımcı olamıyorum. Farklı bir soru sormak ister misiniz?"
            }

    for kalip in HIKAYE_KALIPLARI:
        if kalip.search(metin):
            return {
                "gecti": False,
                "katman": "giris_denetimi",
                "tehdit": "hikaye_manipulasyon",
                #"mesaj": "Rol yapma ve hikaye senaryoları bu sistemde desteklenmiyor."
                "mesaj": "Yalnızca şirket konularında yardımcı olabiliyorum. Başka bir konuda yardımcı olabilir miyim?"
            }

    for kalip in SAHTE_YETKI_KALIPLARI:
        if kalip.search(metin):
            return {
                "gecti": False,
                "katman": "giris_denetimi",
                "tehdit": "sahte_yetki_iddiasi",
                #"mesaj": "Yetki iddiasıyla erişim sağlanamaz."
                "mesaj": "Yalnızca şirket konularında yardımcı olabiliyorum. Başka bir konuda yardımcı olabilir miyim?"
            }

    return {"gecti": True, "katman": "giris_denetimi", "tehdit": None}


# ─────────────────────────────────────────────
# KATMAN 2 — UZUNLUK DENETİMİ
# ─────────────────────────────────────────────

MAKS_INPUT = 500
MAKS_OUTPUT = 2000


def uzunluk_denetimi(metin: str, yon: str = "input") -> dict:
    """Katman 2 — input ve output uzunluklarını ayrı kontrol et."""
    limit = MAKS_INPUT if yon == "input" else MAKS_OUTPUT

    if len(metin) > limit:
        return {
        "gecti": False,
        "katman": "uzunluk_denetimi",
        "tehdit": f"asiri_uzun_{yon}",
        "mesaj": "Sorunuzu daha iyi anlayabilmem için biraz daha kısa ve öz yazar mısınız?"
    }

    return {"gecti": True, "katman": "uzunluk_denetimi", "tehdit": None}


# ─────────────────────────────────────────────
# KATMAN 3 — ÇIKIŞ DENETİMİ
# ─────────────────────────────────────────────

def _ters_metin_mi(metin: str) -> bool:
    """Tersine çevrilmiş metin tespiti."""
    temiz = metin.replace(" ", "").lower()
    if len(temiz) < 10:
        return False
    ters = temiz[::-1]
    tehlikeli = ["sifre", "token", "admin", "secret", "password", "gizli"]
    return any(k in ters for k in tehlikeli)


def _akrostis_mi(metin: str) -> bool:
    """Satır başı harfleriyle gizli mesaj tespiti."""
    satirlar = [s.strip() for s in metin.strip().splitlines() if s.strip()]
    if len(satirlar) < 4:
        return False
    bas_harfler = "".join(s[0].lower() for s in satirlar if s)
    tehlikeli = ["sifre", "token", "admin", "hack", "pass"]
    return any(k in bas_harfler for k in tehlikeli)


def _asiri_bosluk_mu(metin: str) -> bool:
    """Kelimeler arasına bırakılan aşırı boşluk tespiti."""
    if re.search(r" {3,}", metin):
        return True
    if re.search(r"(\b\w \w \w\b)", metin):
        return True
    return False


def _pii_var_mi(metin: str) -> list:
    """Kişisel veri sızıntısı tespiti."""
    sorunlar = []
    if re.search(r"\b\d{11}\b", metin):
        sorunlar.append("tc_kimlik")
    if re.search(r"\b\d{4,6}\s*(TL|₺|lira)\b", metin, re.I):
        sorunlar.append("maas_bilgisi")
    if re.search(r"\b(\+90|0)?\s?5\d{2}\s?\d{3}\s?\d{2}\s?\d{2}\b", metin):
        sorunlar.append("telefon")
    return sorunlar


def cikis_denetimi(metin: str) -> dict:
    """Katman 3 — PII, ters metin, akrostiş, aşırı boşluk, uzunluk kontrolü."""
    sorunlar = []

    pii = _pii_var_mi(metin)
    sorunlar.extend(pii)

    if _ters_metin_mi(metin):
        sorunlar.append("ters_metin")

    if _akrostis_mi(metin):
        sorunlar.append("akrostis")

    if _asiri_bosluk_mu(metin):
        sorunlar.append("asiri_bosluk")

    uzunluk = uzunluk_denetimi(metin, yon="output")
    if not uzunluk["gecti"]:
        sorunlar.append("asiri_uzun_output")

    return {
        "temiz": len(sorunlar) == 0,
        "katman": "cikis_denetimi",
        "sorunlar": sorunlar
    }


# ─────────────────────────────────────────────
# KURAL İHLAL TAKİP SİSTEMİ — BAN
# ─────────────────────────────────────────────

_ihlal_kaydi: dict[str, list] = {}

BAN_SURESI_DAKIKA = 60
UYARI_ESIGI = 2


def ihlal_kaydet(kullanici_id: str) -> dict:
    """İhlali kaydet, gerekirse banla."""
    simdi = datetime.now()

    if kullanici_id not in _ihlal_kaydi:
        _ihlal_kaydi[kullanici_id] = []

    # Son 1 saatteki ihlalleri tut
    _ihlal_kaydi[kullanici_id] = [
        z for z in _ihlal_kaydi[kullanici_id]
        if simdi - z < timedelta(hours=1)
    ]

    _ihlal_kaydi[kullanici_id].append(simdi)
    ihlal_sayisi = len(_ihlal_kaydi[kullanici_id])

    if ihlal_sayisi > UYARI_ESIGI:
        return {
            "durum": "banlandi",
            "ihlal_sayisi": ihlal_sayisi,
            #"mesaj": f"Şu an size yardımcı olamıyorum. Lütfen daha sonra tekrar deneyin.",
            "mesaj": f"Çok fazla güvenlik ihlali. {BAN_SURESI_DAKIKA} dakika erişiminiz askıya alındı.",
        }
    elif ihlal_sayisi == UYARI_ESIGI:
        return {
            "durum": "son_uyari",
            "ihlal_sayisi": ihlal_sayisi,
            "mesaj": "⚠️ Son uyarı: Bir daha ihlal tespit edilirse 1 saat erişiminiz askıya alınacak.",
            #"mesaj": "Yalnızca şirket konularında yardımcı olabiliyorum. Başka bir konuda yardımcı olabilir miyim?",
        }
    
    else:
        return {
            "durum": "uyarildi",
            "ihlal_sayisi": ihlal_sayisi,
            "mesaj": "⚠️ Güvenlik politikası ihlali. Lütfen sistemi uygun şekilde kullanın.",
            #"mesaj": "Bu konuda size yardımcı olamıyorum. Farklı bir soru sormak ister misiniz?",
        }


def ban_kontrol(kullanici_id: str) -> dict:
    """Kullanıcı hâlâ banlı mı?"""
    if kullanici_id not in _ihlal_kaydi:
        return {"banli": False}

    simdi = datetime.now()
    son_ihlaller = [
        z for z in _ihlal_kaydi[kullanici_id]
        if simdi - z < timedelta(hours=1)
    ]

    if len(son_ihlaller) > UYARI_ESIGI:
        en_son = max(son_ihlaller)
        ban_bitis = en_son + timedelta(minutes=BAN_SURESI_DAKIKA)
        if simdi < ban_bitis:
            kalan = int((ban_bitis - simdi).total_seconds() / 60)
            return {
                "banli": True,
                "mesaj": f"Erişiminiz askıya alındı. {kalan} dakika sonra tekrar deneyin.",
                "kalan_dakika": kalan
            }

    return {"banli": False}


# ─────────────────────────────────────────────
# ANA KONTROL — GİRİŞ İÇİN
# ─────────────────────────────────────────────

def tam_giris_kontrolu(metin: str, kullanici_id: str = "anonim") -> dict:
    """Katman 1 + Katman 2 sırayla çalışır. İhlalde ban sistemini tetikler."""

    # Önce ban kontrolü
    ban = ban_kontrol(kullanici_id)
    if ban["banli"]:
        return {
            "gecti": False,
            "katman": "ban_kontrol",
            "tehdit": "banlandi",
            "mesaj": ban["mesaj"]
        }

    # Katman 2 — uzunluk
    uzunluk = uzunluk_denetimi(metin, yon="input")
    if not uzunluk["gecti"]:
        return uzunluk

    # Katman 1 — içerik
    giris = giris_denetimi(metin)
    if not giris["gecti"]:
        ceza = ihlal_kaydet(kullanici_id)
        giris["ceza"] = ceza
        giris["mesaj"] = ceza["mesaj"]
        return giris

    return {"gecti": True, "tehdit": None, "mesaj": "Temiz"}