# ⚡ Hamming Error-Correcting Code Simülatörü

> **BLM230 Bilgisayar Mimarisi — Dönem Projesi**  
> Bursa Teknik Üniversitesi

---

## 📌 Proje Hakkında

Bu proje, **Hamming Error-Correcting Code** (Hamming Hata Düzeltme Kodu) algoritmasını görsel ve etkileşimli biçimde simüle eden bir masaüstü uygulamasıdır. Belleğe yazılan verilerde oluşabilecek tek-bit hatalarını otomatik olarak tespit edip düzelten Hamming kodunun nasıl çalıştığını adım adım gösterir.

---

## 🖼️ Ekran Görüntüsü

```
┌─────────────────────────────┬─────────────────────────────┐
│   📥 VERİ GİRİŞİ & ENCODE   │  💾 BELLEK / HATA / DÜZELTME│
│                             │                             │
│  Bit Boyutu: ● 8  ○ 16 ○ 32 │  [0][0][1][0][1][1][1][1].. │
│  Veri: [10110011______]      │                             │
│                             │  🔍 SENDROMU HESAPLA        │
│  🔐 ENCODE & BELLEĞE YAZ    │  ✅ HATAYI DÜZELT           │
│                             │                             │
│  🔎 PARITY HESABINI GÖSTER  │  Sonuç: Hata düzeltildi!    │
└─────────────────────────────┴─────────────────────────────┘
│ 📋 İŞLEM KAYITLARI                                        │
└────────────────────────────────────────────────────────────┘
```

---

## 🚀 Özellikler

- ✅ **8, 16 ve 32 bit** veri desteği
- ✅ Hamming kodunu hesaplayıp **renkli görsel** olarak gösterir
  - 🟣 Mor kutular → Parity bitleri
  - 🔵 Mavi kutular → Veri bitleri
- ✅ Herhangi bir bite **tıklayarak yapay hata** oluşturma
- ✅ **Çoklu hata tespiti** — 2+ bit aynı anda bozulursa uyarı verir
- ✅ **Sendrom hesaplama** ile hatalı biti otomatik bulma
- ✅ Hatalı biti **otomatik düzeltme** ve orijinal veriyi kurtarma
- ✅ **Parity hesabını adım adım** gösteren ayrıntılı pencere (XOR zinciri)
- ✅ **Veri karşılaştırma** tablosu (orijinal vs kurtarılan)
- ✅ Tüm işlemlerin takip edilebildiği **işlem kayıt alanı**
- ✅ Kaydırmalı bit görüntüsü (32 bit için otomatik scroll)

---

## 🧠 Hamming Kodu Nasıl Çalışır?

### 1. Encode (Veri Yazma)
Kullanıcının girdiği veriye **parity bitleri** eklenerek Hamming kodu oluşturulur ve belleğe yazılır. Parity bitleri 2'nin kuvveti olan pozisyonlara (1, 2, 4, 8, 16...) yerleştirilir.

### 2. Hata Oluşturma
Bellekteki herhangi bir bit yapay olarak ters çevrilir. Bu gerçek hayatta kozmik ışın çarpması, voltaj dalgalanması gibi fiziksel nedenlerle oluşan bit hatalarını simüle eder.

### 3. Sendrom Hesaplama
Bellekten okunan veri üzerinde XOR işlemleri yapılarak **sendrom** hesaplanır. Sendrom değeri:
- `0` → Hata yok
- `> 0` → Hatalı bitin pozisyonunu doğrudan gösterir

### 4. Hata Düzeltme
Sendromun işaret ettiği bit ters çevrilerek hata düzeltilir. Parity bitleri çıkarıldığında orijinal veri kurtarılır.

```
Örnek (8 bit veri: 10110011):

Hamming kodu → 0 0 1 1 0 1 1 0 0 1 1 (12 bit, 4 parity)
               P P D P D D D P D D D
               1 2 3 4 5 6 7 8 9 ...

Bit 5 bozulursa → Sendrom = 5 → Bit 5 düzeltilir → Veri kurtarılır ✓
```

---

## 🛠️ Kurulum ve Çalıştırma

### Gereksinimler

- Python 3.6 veya üzeri
- Tkinter (Python ile birlikte gelir, ayrıca kurulum gerekmez)

### Çalıştırma

```bash
# Projeyi klonlayın veya dosyayı indirin
git clone https://github.com/kullanici/hamming-simulator.git
cd hamming-simulator

# Programı çalıştırın
python hamming_simulator.py
```

### Windows için

```
python hamming_simulator.py
```

### Linux / macOS için

```bash
python3 hamming_simulator.py
```

> ⚠️ Tkinter kurulu değilse (bazı Linux dağıtımlarında):
> ```bash
> sudo apt-get install python3-tk
> ```

---

## 📖 Kullanım Kılavuzu

| Adım | Yapılacak İşlem |
|------|----------------|
| 1 | Bit boyutunu seçin: **8**, **16** veya **32** |
| 2 | İkili veri girin (örn: `10110011` for 8-bit) |
| 3 | **ENCODE & BELLEĞE YAZ** butonuna tıklayın |
| 4 | Hamming kodunun renklı gösterimini inceleyin |
| 5 | İsteğe bağlı: **PARITY HESABINI GÖSTER** ile adımları görün |
| 6 | Bellekteki herhangi bir bite tıklayarak hata oluşturun |
| 7 | **SENDROMU HESAPLA** ile hatalı biti bulun |
| 8 | **HATAYI DÜZELT** ile orijinal veriyi kurtarın |

---

## 📁 Dosya Yapısı

```
hamming-simulator/
│
└── hamming_simulator.py    # Ana uygulama (tek dosya)
```

---

## 🔬 Teknik Detaylar

| Parametre | Değer |
|-----------|-------|
| Desteklenen veri boyutları | 8, 16, 32 bit |
| 8 bit için toplam bit | 12 bit (4 parity + 8 veri) |
| 16 bit için toplam bit | 21 bit (5 parity + 16 veri) |
| 32 bit için toplam bit | 38 bit (6 parity + 32 veri) |
| Hata düzeltme kapasitesi | Tek bit hatası |
| Hata tespit kapasitesi | Çoklu bit hatası (düzeltilemez) |

---

## 🎨 Arayüz Renk Kodları

| Renk | Anlam |
|------|-------|
| 🟣 Mor | Parity biti |
| 🔵 Mavi | Veri biti |
| 🔴 Kırmızı | Hatalı bit |
| 🟢 Yeşil | Doğru / Başarılı |
| 🟡 Sarı | Uyarı / İşlem bekleniyor |

---

## 📚 Kaynaklar

- Stallings, W. (2016). *Computer Organization and Architecture* (10th ed.). Pearson.
- Hamming, R. W. (1950). Error detecting and error correcting codes. *Bell System Technical Journal*, 29(2), 147–160.
- [Wikipedia — Hamming Code](https://en.wikipedia.org/wiki/Hamming_code)

---


## 👨‍💻 Geliştirici

**BLM230 Bilgisayar Mimarisi Dersi**  
24360859049- Arif Kemal Şeremet
Bursa Teknik Üniversitesi — Bilgisayar Mühendisliği  

---

> *"The purpose of error correction is not to detect the error, but to correct it."*  
> — Richard W. Hamming