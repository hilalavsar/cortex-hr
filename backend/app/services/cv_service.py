from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid

client = QdrantClient("localhost", port=6333)
model = SentenceTransformer("all-MiniLM-L6-v2")
CV_KOLEKSIYON = "cv_havuzu"

def cv_koleksiyon_hazirla():
    mevcut = [k.name for k in client.get_collections().collections]
    if CV_KOLEKSIYON not in mevcut:
        client.create_collection(
            collection_name=CV_KOLEKSIYON,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

def cv_metni_cikart(dosya_adi: str, icerik: bytes) -> str:
    if dosya_adi.lower().endswith(".pdf"):
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(icerik))
        return "\n".join(sayfa.extract_text() or "" for sayfa in reader.pages)
    elif dosya_adi.lower().endswith((".docx", ".doc")):
        from docx import Document
        import io
        doc = Document(io.BytesIO(icerik))
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Desteklenmeyen dosya formatı. Sadece PDF veya DOCX kabul edilir.")

def _parcala(metin: str, parca_boyutu: int = 300) -> list[str]:
    kelimeler = metin.split()
    return [
        " ".join(kelimeler[i : i + parca_boyutu])
        for i in range(0, len(kelimeler), parca_boyutu)
        if kelimeler[i : i + parca_boyutu]
    ]

def cv_yukle(dosya_adi: str, metin: str, yukleyen_id: str) -> int:
    cv_koleksiyon_hazirla()
    parcalar = _parcala(metin)
    noktalar = []
    for parca in parcalar:
        vektor = model.encode(parca).tolist()
        noktalar.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vektor,
                payload={
                    "metin": parca,
                    "kaynak": dosya_adi,
                    "yukleyen": yukleyen_id,
                },
            )
        )
    if noktalar:
        client.upsert(collection_name=CV_KOLEKSIYON, points=noktalar)
    return len(noktalar)

def cv_ara(soru: str, limit: int = 5) -> list[dict]:
    cv_koleksiyon_hazirla()
    vektor = model.encode(soru).tolist()
    sonuclar = client.query_points(
        collection_name=CV_KOLEKSIYON,
        query=vektor,
        limit=limit,
    ).points
    return [
        {
            "metin": s.payload["metin"],
            "kaynak": s.payload["kaynak"],
            "yukleyen": s.payload.get("yukleyen", ""),
            "skor": round(s.score, 2),
        }
        for s in sonuclar
    ]

def cv_baglan_olustur(sonuclar: list[dict]) -> str:
    if not sonuclar:
        return "Eşleşen CV bulunamadı."
    return "\n\n".join(
        f"[CV: {s['kaynak']}]\n{s['metin']}" for s in sonuclar
    )
