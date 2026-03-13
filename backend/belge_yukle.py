from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import os
import uuid

# Bağlantılar
client = QdrantClient("localhost", port=6333)
model = SentenceTransformer("all-MiniLM-L6-v2")

KOLEKSIYON = "cortex_hr"

# Koleksiyon oluştur
def koleksiyon_olustur():
    mevcut = [k.name for k in client.get_collections().collections]
    if KOLEKSIYON not in mevcut:
        client.create_collection(
            collection_name=KOLEKSIYON,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print(f"Koleksiyon oluşturuldu: {KOLEKSIYON}")
    else:
        print(f"Koleksiyon zaten var: {KOLEKSIYON}")

# Belgeyi parçalara böl
def parcala(metin: str, parca_boyutu: int = 300) -> list[str]:
    kelimeler = metin.split()
    parcalar = []
    i = 0
    while i < len(kelimeler):
        parca = " ".join(kelimeler[i:i + parca_boyutu])
        parcalar.append(parca)
        i += parca_boyutu
    return parcalar

# Belgeleri yükle
def belgeleri_yukle(klasor: str):
    koleksiyon_olustur()
    noktalar = []

    for dosya in os.listdir(klasor):
        if dosya.endswith(".md"):
            yol = os.path.join(klasor, dosya)
            metin = open(yol, encoding="utf-8-sig").read()
            parcalar = parcala(metin)

            for parca in parcalar:
                vektor = model.encode(parca).tolist()
                noktalar.append(
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=vektor,
                        payload={
                            "metin": parca,
                            "kaynak": dosya
                        }
                    )
                )
            print(f"İşlendi: {dosya} → {len(parcalar)} parça")

    client.upsert(collection_name=KOLEKSIYON, points=noktalar)
    print(f"\nToplam {len(noktalar)} parça Qdrant'a yüklendi.")

if __name__ == "__main__":
    belgeleri_yukle("../data/hr_docs")