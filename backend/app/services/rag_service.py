from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient("localhost", port=6333)
model = SentenceTransformer("all-MiniLM-L6-v2")
KOLEKSIYON = "cortex_hr"

def ilgili_belgeleri_bul(soru: str, limit: int = 3) -> list[dict]:
    vektor = model.encode(soru).tolist()
    sonuclar = client.query_points(
        collection_name=KOLEKSIYON,
        query=vektor,
        limit=limit
    ).points
    return [
        {
            "metin": s.payload["metin"],
            "kaynak": s.payload["kaynak"],
            "skor": round(s.score, 2)
        }
        for s in sonuclar
    ]

def baglan_olustur(belgeler: list[dict]) -> str:
    if not belgeler:
        return "İlgili belge bulunamadı."
    parcalar = []
    for b in belgeler:
        parcalar.append(f"[Kaynak: {b['kaynak']}]\n{b['metin']}")
    return "\n\n".join(parcalar)