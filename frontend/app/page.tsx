"use client";
type Mesaj = {
  rol: string;
  metin: string;
  kaynaklar?: string[];
};
import { useState } from "react";

export default function Home() {
  const [girisYapildi, setGirisYapildi] = useState(false);
  const [token, setToken] = useState("");
  const [kullaniciAdi, setKullaniciAdi] = useState("");
  const [sifre, setSifre] = useState("");
  const [mesajlar, setMesajlar] = useState<Mesaj[]>([]);
  const [yeniMesaj, setYeniMesaj] = useState("");
  const [yukleniyor, setYukleniyor] = useState(false);
  const [hata, setHata] = useState("");

  async function girisYap() {
    setHata("");
    try {
      const yanit = await fetch("http://192.168.20.1:8000/api/v1/auth/giris", {
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
    const kullaniciMesaji = { rol: "kullanici", metin: yeniMesaj };
    setMesajlar((m) => [...m, kullaniciMesaji]);
    setYeniMesaj("");
    setYukleniyor(true);

    try {
      const yanit = await fetch("http://192.168.20.1:8000/api/v1/chat/sor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mesaj: yeniMesaj, kullanici_id: kullaniciAdi }),
      });
      const veri = await yanit.json();
      if (!yanit.ok) {
        setMesajlar((m) => [...m, { rol: "asistan", metin: veri.detail }]);
      } else {
        setMesajlar((m) => [
          ...m,
          {
            rol: "asistan",
            metin: veri.cevap,
            kaynaklar: veri.kaynaklar,
          },
        ]);
      }
    } catch {
      setMesajlar((m) => [
        ...m,
        { rol: "asistan", metin: "Sunucuya bağlanılamadı." },
      ]);
    } finally {
      setYukleniyor(false);
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
        <div>
          <h1 className="text-white font-bold">Cortex HR</h1>
          <p className="text-gray-400 text-xs">Şirket içi asistan</p>
        </div>
        <button
          className="text-gray-400 hover:text-white text-sm transition"
          onClick={() => setGirisYapildi(false)}
        >
          Çıkış
        </button>
      </div>

      {/* Mesajlar */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {mesajlar.map((m, i) => (
          <div
            key={i}
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

      {/* Mesaj kutusu */}
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
    </div>
  );
}