"use client";
type Mesaj = {
  rol: string;
  metin: string;
  kaynaklar?: string[];
};
import { useState, useRef } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://192.168.20.1:8000/api/v1";

export default function Home() {
  const [girisYapildi, setGirisYapildi] = useState(false);
  const [token, setToken] = useState("");
  const [kullaniciRol, setKullaniciRol] = useState("");
  const [kullaniciAdi, setKullaniciAdi] = useState("");
  const [sifre, setSifre] = useState("");
  const [mesajlar, setMesajlar] = useState<Mesaj[]>([]);
  const [yeniMesaj, setYeniMesaj] = useState("");
  const [yukleniyor, setYukleniyor] = useState(false);
  const [hata, setHata] = useState("");

  // CV paneli state
  const [aktifSekme, setAktifSekme] = useState<"chat" | "cv">("chat");
  const [cvIslem, setCvIslem] = useState<"yukle" | "ozet" | "ara">("yukle");
  const [cvYukleniyor, setCvYukleniyor] = useState(false);
  const [cvSonuc, setCvSonuc] = useState("");
  const [cvAramaSorusu, setCvAramaSorusu] = useState("");
  const dosyaRef = useRef<HTMLInputElement>(null);

  async function girisYap() {
    setHata("");
    try {
      const yanit = await fetch(`${API}/auth/giris`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ kullanici_adi: kullaniciAdi, sifre: sifre }),
      });
      const veri = await yanit.json();
      if (!yanit.ok) {
        setHata("Kullanıcı adı veya şifre hatalı.");
        return;
      }
      setToken(veri.token);
      setKullaniciRol(veri.rol);
      setGirisYapildi(true);
      setMesajlar([
        {
          rol: "asistan",
          metin: `Merhaba ${veri.ad}! Ben Cortex HR asistanı. Size nasıl yardımcı olabilirim?`,
        },
      ]);
    } catch {
      setHata("Sunucuya bağlanılamadı.");
    }
  }

  async function mesajGonder() {
    if (!yeniMesaj.trim() || yukleniyor) return;
    const kullaniciMesaji: Mesaj = { rol: "kullanici", metin: yeniMesaj };
    setMesajlar((m: Mesaj[]) => [...m, kullaniciMesaji]);
    setYeniMesaj("");
    setYukleniyor(true);

    try {
      const yanit = await fetch(`${API}/chat/sor`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mesaj: yeniMesaj, kullanici_id: kullaniciAdi }),
      });
      const veri = await yanit.json();
      if (yanit.ok) {
        setMesajlar((m: Mesaj[]) => [
          ...m,
          { rol: "asistan", metin: veri.cevap, kaynaklar: veri.kaynaklar },
        ]);
      } else {
        setMesajlar((m: Mesaj[]) => [...m, { rol: "asistan", metin: veri.detail }]);
      }
    } catch {
      setMesajlar((m: Mesaj[]) => [...m, { rol: "asistan", metin: "Sunucuya bağlanılamadı." }]);
    } finally {
      setYukleniyor(false);
    }
  }

  async function cvDosyaIsle(endpoint: "yukle" | "ozet") {
    const dosya = dosyaRef.current?.files?.[0];
    if (!dosya) {
      setCvSonuc("Lütfen bir dosya seçin.");
      return;
    }
    setCvYukleniyor(true);
    setCvSonuc("");
    const form = new FormData();
    form.append("dosya", dosya);
    try {
      const yanit = await fetch(`${API}/cv/${endpoint}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });
      const veri = await yanit.json();
      if (!yanit.ok) {
        setCvSonuc(`Hata: ${veri.detail}`);
      } else if (endpoint === "yukle") {
        setCvSonuc(veri.mesaj);
      } else {
        setCvSonuc(veri.ozet);
      }
    } catch {
      setCvSonuc("Sunucuya bağlanılamadı.");
    } finally {
      setCvYukleniyor(false);
    }
  }

  async function cvAra() {
    if (!cvAramaSorusu.trim()) return;
    setCvYukleniyor(true);
    setCvSonuc("");
    try {
      const yanit = await fetch(`${API}/cv/ara`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ soru: cvAramaSorusu }),
      });
      const veri = await yanit.json();
      if (yanit.ok) {
        const kaynaklar =
          veri.eslesen_cvler?.length > 0
            ? `\n\nEşleşen CV'ler: ${veri.eslesen_cvler.join(", ")}`
            : "";
        setCvSonuc(veri.cevap + kaynaklar);
      } else {
        setCvSonuc(`Hata: ${veri.detail}`);
      }
    } catch {
      setCvSonuc("Sunucuya bağlanılamadı.");
    } finally {
      setCvYukleniyor(false);
    }
  }

  if (!girisYapildi) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="bg-gray-900 p-8 rounded-2xl w-full max-w-sm shadow-xl">
          <h1 className="text-2xl font-bold text-white mb-2">Cortex HR</h1>
          <p className="text-gray-400 text-sm mb-6">Şirket içi asistan</p>
          {hata && <p className="text-red-400 text-sm mb-4">{hata}</p>}
          <input
            className="w-full bg-gray-800 text-white rounded-lg px-4 py-2 mb-3 outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Kullanıcı adı"
            value={kullaniciAdi}
            onChange={(e) => setKullaniciAdi(e.target.value)}
          />
          <input
            className="w-full bg-gray-800 text-white rounded-lg px-4 py-2 mb-6 outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Şifre"
            type="password"
            value={sifre}
            onChange={(e) => setSifre(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && girisYap()}
          />
          <button
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition"
            onClick={girisYap}
          >
            Giriş Yap
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      {/* Üst bar */}
      <div className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="text-white font-bold">Cortex HR</h1>
            <p className="text-gray-400 text-xs">Şirket içi asistan</p>
          </div>
          {kullaniciRol === "ik" && (
            <div className="flex gap-1 bg-gray-800 rounded-lg p-1">
              <button
                className={`px-3 py-1 rounded-md text-sm transition ${
                  aktifSekme === "chat"
                    ? "bg-blue-600 text-white"
                    : "text-gray-400 hover:text-white"
                }`}
                onClick={() => setAktifSekme("chat")}
              >
                Sohbet
              </button>
              <button
                className={`px-3 py-1 rounded-md text-sm transition ${
                  aktifSekme === "cv"
                    ? "bg-blue-600 text-white"
                    : "text-gray-400 hover:text-white"
                }`}
                onClick={() => setAktifSekme("cv")}
              >
                CV İnceleme
              </button>
            </div>
          )}
        </div>
        <button
          className="text-gray-400 hover:text-white text-sm transition"
          onClick={() => {
            setGirisYapildi(false);
            setToken("");
            setKullaniciRol("");
            setAktifSekme("chat");
          }}
        >
          Çıkış
        </button>
      </div>

      {/* ── SOHBET SEKMESİ ── */}
      {aktifSekme === "chat" && (
        <>
          <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
            {mesajlar.map((m, i) => (
              <div
                key={`msg-${i}-${m.rol}`}
                className={`flex ${m.rol === "kullanici" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-lg px-4 py-3 rounded-2xl text-sm ${
                    m.rol === "kullanici"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-800 text-gray-100"
                  }`}
                >
                  <p>{m.metin}</p>
                </div>
              </div>
            ))}
            {yukleniyor && (
              <div className="flex justify-start">
                <div className="bg-gray-800 text-gray-400 px-4 py-3 rounded-2xl text-sm">
                  Yanıt hazırlanıyor...
                </div>
              </div>
            )}
          </div>
          <div className="bg-gray-900 border-t border-gray-800 px-4 py-4 flex gap-3">
            <input
              className="flex-1 bg-gray-800 text-white rounded-xl px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              placeholder="Bir şey sorun..."
              value={yeniMesaj}
              onChange={(e) => setYeniMesaj(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && mesajGonder()}
            />
            <button
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition disabled:opacity-50"
              onClick={mesajGonder}
              disabled={yukleniyor}
            >
              Gönder
            </button>
          </div>
        </>
      )}

      {/* ── CV İNCELEME SEKMESİ (sadece İK) ── */}
      {aktifSekme === "cv" && kullaniciRol === "ik" && (
        <div className="flex-1 overflow-y-auto px-4 py-6 max-w-2xl mx-auto w-full">
          {/* İşlem seçici */}
          <div className="flex gap-2 mb-6">
            {(["yukle", "ozet", "ara"] as const).map((islem) => (
              <button
                key={islem}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition ${
                  cvIslem === islem
                    ? "bg-blue-600 text-white"
                    : "bg-gray-800 text-gray-400 hover:text-white"
                }`}
                onClick={() => {
                  setCvIslem(islem);
                  setCvSonuc("");
                }}
              >
                {islem === "yukle" && "CV Yükle"}
                {islem === "ozet" && "CV Özetle"}
                {islem === "ara" && "CV Ara"}
              </button>
            ))}
          </div>

          {/* CV Yükle */}
          {cvIslem === "yukle" && (
            <div className="bg-gray-900 rounded-2xl p-6 space-y-4">
              <h2 className="text-white font-semibold">CV Havuzuna Yükle</h2>
              <p className="text-gray-400 text-sm">
                PDF veya DOCX formatındaki CV'yi havuza ekler. Daha sonra arama
                yapılabilir.
              </p>
              <input
                ref={dosyaRef}
                type="file"
                accept=".pdf,.docx"
                className="w-full text-gray-300 text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-600 file:text-white file:text-sm file:cursor-pointer hover:file:bg-blue-700"
              />
              <button
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium transition disabled:opacity-50"
                onClick={() => cvDosyaIsle("yukle")}
                disabled={cvYukleniyor}
              >
                {cvYukleniyor ? "Yükleniyor..." : "Havuza Ekle"}
              </button>
            </div>
          )}

          {/* CV Özetle */}
          {cvIslem === "ozet" && (
            <div className="bg-gray-900 rounded-2xl p-6 space-y-4">
              <h2 className="text-white font-semibold">CV Özetle</h2>
              <p className="text-gray-400 text-sm">
                Seçilen CV'yi Mistral ile analiz eder ve kısa bir değerlendirme
                sunar.
              </p>
              <input
                ref={dosyaRef}
                type="file"
                accept=".pdf,.docx"
                className="w-full text-gray-300 text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-600 file:text-white file:text-sm file:cursor-pointer hover:file:bg-blue-700"
              />
              <button
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium transition disabled:opacity-50"
                onClick={() => cvDosyaIsle("ozet")}
                disabled={cvYukleniyor}
              >
                {cvYukleniyor ? "Analiz ediliyor..." : "Özetle"}
              </button>
            </div>
          )}

          {/* CV Ara */}
          {cvIslem === "ara" && (
            <div className="bg-gray-900 rounded-2xl p-6 space-y-4">
              <h2 className="text-white font-semibold">CV Havuzunda Ara</h2>
              <p className="text-gray-400 text-sm">
                Yüklenmiş CV'ler arasında anlam bazlı arama yapar.
              </p>
              <input
                className="w-full bg-gray-800 text-white rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                placeholder="Örn: 5 yıl deneyimli Python geliştirici"
                value={cvAramaSorusu}
                onChange={(e) => setCvAramaSorusu(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && cvAra()}
              />
              <button
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium transition disabled:opacity-50"
                onClick={cvAra}
                disabled={cvYukleniyor}
              >
                {cvYukleniyor ? "Aranıyor..." : "Ara"}
              </button>
            </div>
          )}

          {/* Sonuç alanı */}
          {cvSonuc && (
            <div className="mt-4 bg-gray-800 rounded-2xl p-5">
              <p className="text-xs text-gray-500 mb-2 uppercase tracking-wide">Sonuç</p>
              <p className="text-gray-100 text-sm whitespace-pre-wrap">{cvSonuc}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
