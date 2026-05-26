import tkinter as tk
from tkinter import messagebox

# ============================================================
#   HAMMING KODU - TEMEL ALGORITMA FONKSIYONLARI
#   Bu bolumde hicbir arayuz kodu yok.
#   Sadece matematiksel hesaplamalar var.
# ============================================================

def kac_parity_biti_gerekir(veri_bit_sayisi):
    """
    Verilen veri bit sayisi icin kac tane parity (kontrol) biti
    gerektigini hesaplar.

    Kural: 2^r  >=  veri_bit_sayisi + r + 1
    r yi 0 dan baslayip bu kural saglanana kadar arttiririz.

    Ornek: 8 bitlik veri icin r=4 parity biti gerekir.
    """
    r = 0
    while (2 ** r) < (veri_bit_sayisi + r + 1):
        r += 1
    return r


def parity_pozisyonlarini_bul(toplam_bit_sayisi):
    """
    Hamming kodunda parity bitleri 1, 2, 4, 8, 16 ... gibi
    2'nin kuvveti olan pozisyonlara yerlestirilir.

    Bu fonksiyon o pozisyonlarin listesini dondurur.
    Ornek: toplam 12 bit icin -> [1, 2, 4, 8]
    """
    pozisyonlar = []
    i = 1
    while i <= toplam_bit_sayisi:
        pozisyonlar.append(i)
        i *= 2  # her seferinde 2 ile carp: 1->2->4->8->...
    return pozisyonlar


def hamming_encode(veri_bitleri):
    """
    Kullanicinin girdigi ikili veriyi Hamming koduna donusturur.

    Adimlar:
    1) Kac parity biti gerektigini hesapla
    2) Bos bir dizi olustur (toplam uzunluk = veri + parity)
    3) Veri bitlerini parity olmayan pozisyonlara yerlestir
    4) Her parity bitini XOR ile hesapla
    """

    # --- Adim 1: Boyutlari hesapla ---
    veri_uzunlugu = len(veri_bitleri)
    parity_sayisi = kac_parity_biti_gerekir(veri_uzunlugu)
    toplam_uzunluk = veri_uzunlugu + parity_sayisi

    # --- Adim 2: Bos dizi olustur (index 0 kullanilmayacak, 1'den baslar) ---
    # Neden +1? Cunku pozisyonlar 1'den basliyor, 0 indeksi bos birakiyoruz.
    hamming_dizisi = [0] * (toplam_uzunluk + 1)

    # --- Adim 3: Veri bitlerini dogru pozisyonlara yerlestir ---
    # Parity pozisyonlari (1,2,4,8...) bos kalacak, diger pozisyonlara veri gidecek
    veri_indeksi = 0
    for pozisyon in range(1, toplam_uzunluk + 1):
        # Eger bu pozisyon 2'nin kuvveti ise -> parity yeri, atliyoruz
        # 2'nin kuvveti kontrolu: sayi & (sayi-1) == 0 ise 2'nin kuvvetidir
        if pozisyon & (pozisyon - 1) != 0:
            # 2'nin kuvveti degil -> buraya veri biti gidecek
            hamming_dizisi[pozisyon] = int(veri_bitleri[veri_indeksi])
            veri_indeksi += 1

    # --- Adim 4: Her parity bitini hesapla ---
    # Her parity biti, belirli pozisyonlarin XOR'u olacak
    for i in range(parity_sayisi):
        parity_pos = 2 ** i  # 1, 2, 4, 8, ...

        xor_sonucu = 0
        for k in range(1, toplam_uzunluk + 1):
            # Bu pozisyon bu parity bitini etkiliyor mu?
            # Kural: pozisyon & parity_pos != 0 ise etkileniyor
            if k & parity_pos:
                xor_sonucu ^= hamming_dizisi[k]  # XOR ile birlestir

        hamming_dizisi[parity_pos] = xor_sonucu  # hesaplanan parity'yi yerlestir

    # Index 0'i atarak 1'den itibaren dondur
    return hamming_dizisi[1:]


def sendrom_hesapla(alinan_bitler):
    """
    Alinan (bellekteki) Hamming kodunun sendromunu hesaplar.
    Sendrom = hatanin oldugu pozisyon numarasi.

    Sendrom == 0 ise hata yok.
    Sendrom != 0 ise o numarali pozisyonda hata var.

    Nasil calisir:
    Her parity biti kendi sorumlu oldugu pozisyonlarin XOR'unu kontrol eder.
    Eger XOR sonucu 0 degilse, o parity biti bozuk -> sendroma katkida bulunur.
    """
    toplam_uzunluk = len(alinan_bitler)

    # Kac parity biti oldugunu bul
    r = 0
    while (2 ** r) < toplam_uzunluk + 1:
        r += 1

    sendrom = 0
    for i in range(r):
        parity_pos = 2 ** i  # 1, 2, 4, 8, ...

        xor_sonucu = 0
        for k in range(1, toplam_uzunluk + 1):
            if k & parity_pos:
                xor_sonucu ^= alinan_bitler[k - 1]  # dizi 0'dan baslar, -1 yapiyoruz

        # Bu parity bitti hatali cikti ise sendroma parity pozisyonunu ekle
        if xor_sonucu != 0:
            sendrom += parity_pos

    return sendrom  # 0 ise hata yok, diger degerler hatanin pozisyonunu gosterir


def hatayi_duzelt(bitler, hatali_pozisyon):
    """
    Verilen pozisyondaki biti tersine cevirir (0->1 veya 1->0).
    Bu isleme 'bit flip' denir.
    """
    duzeltilmis = bitler[:]  # kopya al, orijinali bozma

    if 0 < hatali_pozisyon <= len(duzeltilmis):
        # XOR ile 1: biti tersine cevirir (0 XOR 1 = 1,  1 XOR 1 = 0)
        duzeltilmis[hatali_pozisyon - 1] ^= 1

    return duzeltilmis


# ============================================================
#   ARAYUZ SINIFI - HammingSimulatoru
#   Tkinter ile gorsellestirme burada yapiliyor.
#   Tum buton, etiket, cerceve islemleri bu sinifin icinde.
# ============================================================

class HammingSimulatoru:

    def __init__(self, ana_pencere):
        """
        Uygulama ilk acildiginda bu fonksiyon calisir.
        Degiskenleri sifirlar ve arayuzu kurar.
        """
        self.pencere = ana_pencere
        self.pencere.title("Hamming Hata Duzeltme Simulatoru")
        self.pencere.geometry("950x750")
        self.pencere.configure(bg="#1a1a2e")
        self.pencere.resizable(True, True)

        # --- Renk tanimi ---
        # Tum renkler burada tanimli, kod icinde tekrar tekrar yazmiyoruz
        self.renkler = {
            "arkaplan":       "#1a1a2e",   # koyu lacivert - genel arka plan
            "panel":          "#16213e",   # biraz daha acik panel rengi
            "vurgu":          "#0f3460",   # mavi ton - giris kutulari vb.
            "hata_rengi":     "#e94560",   # kirmizi - hata gostergesi
            "yesil":          "#00b894",   # yesil - basarili islem
            "sari":           "#fdcb6e",   # sari - uyari / parity bitleri
            "yazi":           "#eaeaea",   # beyaza yakin - normal yazi
            "alt_yazi":       "#a0a0b0",   # gri - ikincil bilgiler
            "parity_arka":    "#2d1b4e",   # mor ton - parity bit kutulari
            "veri_arka":      "#1b3a4e",   # mavi ton - veri bit kutulari
            "hata_arka":      "#4e1b1b",   # koyu kirmizi - hatali bit kutusu
        }

        # --- Uygulama degiskenleri ---
        self.bellekteki_bitler = []    # encode sonrasi bellekte duran hamming kodu
        self.orijinal_veri = ""        # kullanicinin girdigi ham veri (sadece 0 ve 1)
        self.bit_butonlari = []        # bellekteki her bite karsilik gelen buton listesi

        # --- Arayuzu kur ---
        self.arayuz_kur()


    # ============================================================
    #   ARAYUZ KURULUM FONKSIYONLARI
    #   _arayuz_kur cagrildiginda tum cerceveler olusturulur.
    # ============================================================

    def arayuz_kur(self):
        """
        Ana pencereyi bolgelere ayirir:
        - Ust: baslik
        - Orta sol: giris ve encode paneli
        - Orta sag: bellek / hata / duzeltme paneli
        - Alt: islem kayitlari (log)
        """

        # --- Baslik bolumu ---
        baslik_cerceve = tk.Frame(self.pencere, bg=self.renkler["arkaplan"])
        baslik_cerceve.pack(fill="x", padx=20, pady=(15, 5))

        tk.Label(baslik_cerceve,
                 text="Hamming Hata Duzeltme Kodu Simulatoru",
                 font=("Consolas", 18, "bold"),
                 fg=self.renkler["hata_rengi"],
                 bg=self.renkler["arkaplan"]).pack()

        tk.Label(baslik_cerceve,
                 text="BLM230 Bilgisayar Mimarisi",
                 font=("Consolas", 10),
                 fg=self.renkler["alt_yazi"],
                 bg=self.renkler["arkaplan"]).pack()

        # --- Orta bolum: iki panel yan yana ---
        orta_cerceve = tk.Frame(self.pencere, bg=self.renkler["arkaplan"])
        orta_cerceve.pack(fill="both", expand=True, padx=20, pady=5)

        # Sol panel: veri girisi ve encode
        sol_panel = tk.Frame(orta_cerceve,
                             bg=self.renkler["panel"],
                             relief="ridge", bd=2)
        sol_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Sag panel: bellek goruntuleme, hata tespiti, duzeltme
        sag_panel = tk.Frame(orta_cerceve,
                             bg=self.renkler["panel"],
                             relief="ridge", bd=2)
        sag_panel.pack(side="left", fill="both", expand=True)

        # Her panelin icini doldur
        self.giris_paneli_kur(sol_panel)
        self.bellek_paneli_kur(sag_panel)

        # --- Alt bolum: log alani ---
        self.log_alani_kur()


    def giris_paneli_kur(self, ust_cerceve):
        """
        Sol paneli doldurur:
        - Bit boyutu secimi (8 / 16 / 32)
        - Veri giris kutusu
        - Encode butonu
        - Hamming kodu gosterimi
        - Parity adim adim butonu
        """

        tk.Label(ust_cerceve,
                 text="Veri Girisi ve Encode",
                 font=("Consolas", 12, "bold"),
                 fg=self.renkler["yesil"],
                 bg=self.renkler["panel"]).pack(pady=(12, 4))

        # --- Bit boyutu secimi ---
        # Kullanici 8, 16 veya 32 bitlik veri girebilir
        bit_secim_cerceve = tk.Frame(ust_cerceve, bg=self.renkler["panel"])
        bit_secim_cerceve.pack(pady=4)

        tk.Label(bit_secim_cerceve,
                 text="Bit Boyutu:",
                 font=("Consolas", 10),
                 fg=self.renkler["yazi"],
                 bg=self.renkler["panel"]).pack(side="left", padx=4)

        self.bit_degiskeni = tk.IntVar(value=8)  # varsayilan 8 bit

        for deger in [8, 16, 32]:
            rb = tk.Radiobutton(bit_secim_cerceve,
                                text=f"{deger} bit",
                                variable=self.bit_degiskeni,
                                value=deger,
                                font=("Consolas", 10),
                                fg=self.renkler["yazi"],
                                bg=self.renkler["panel"],
                                selectcolor=self.renkler["vurgu"],
                                activebackground=self.renkler["panel"],
                                command=self.bit_degistiginde)
            rb.pack(side="left", padx=6)

        # --- Veri giris kutusu ---
        tk.Label(ust_cerceve,
                 text="Ikili Veri Girin (sadece 0 ve 1):",
                 font=("Consolas", 10),
                 fg=self.renkler["alt_yazi"],
                 bg=self.renkler["panel"]).pack(pady=(8, 2))

        giris_satiri = tk.Frame(ust_cerceve, bg=self.renkler["panel"])
        giris_satiri.pack(pady=2)

        self.veri_girisi = tk.Entry(giris_satiri,
                                    width=36,
                                    font=("Consolas", 13),
                                    bg=self.renkler["vurgu"],
                                    fg=self.renkler["yesil"],
                                    insertbackground=self.renkler["yesil"],
                                    relief="flat", bd=4)
        self.veri_girisi.pack(side="left", padx=4)
        # Her tus basiminda girisi kontrol et (sadece 0 ve 1 kabul et)
        self.veri_girisi.bind("<KeyRelease>", self.girisi_dogrula)

        # Kac karakter girildi gostergesi (ornek: "5/8")
        self.uzunluk_etiketi = tk.Label(giris_satiri,
                                         text="0/8",
                                         font=("Consolas", 10),
                                         fg=self.renkler["alt_yazi"],
                                         bg=self.renkler["panel"])
        self.uzunluk_etiketi.pack(side="left")

        # --- Encode butonu ---
        tk.Button(ust_cerceve,
                  text="ENCODE ET ve BELLEGE YAZ",
                  font=("Consolas", 11, "bold"),
                  bg=self.renkler["yesil"],
                  fg="#000000",
                  activebackground="#00a381",
                  relief="flat", bd=0,
                  padx=12, pady=6,
                  cursor="hand2",
                  command=self.encode_et).pack(pady=10)

        # --- Hamming kodu gostergesi ---
        # Encode sonrasi olusturulan hamming kodunu renkli kutularda gosterir
        tk.Label(ust_cerceve,
                 text="Hamming Kodu (Bellege Yazilan):",
                 font=("Consolas", 10),
                 fg=self.renkler["alt_yazi"],
                 bg=self.renkler["panel"]).pack(pady=(6, 2))

        # Yatay kaydirma destekli alan (uzun kodlar icin)
        hamming_dis = tk.Frame(ust_cerceve, bg=self.renkler["panel"])
        hamming_dis.pack(pady=4, padx=10, fill="x")

        hamming_kaydirma = tk.Scrollbar(hamming_dis, orient="horizontal")
        hamming_kaydirma.pack(side="bottom", fill="x")

        hamming_tuval = tk.Canvas(hamming_dis, height=52,
                                   bg=self.renkler["panel"],
                                   highlightthickness=0,
                                   xscrollcommand=hamming_kaydirma.set)
        hamming_tuval.pack(side="top", fill="x")
        hamming_kaydirma.config(command=hamming_tuval.xview)

        # Canvas icine bir Frame koyduk, bit kutulari buraya eklenecek
        self.hamming_gosterge = tk.Frame(hamming_tuval, bg=self.renkler["panel"])
        hamming_tuval.create_window((0, 0), window=self.hamming_gosterge, anchor="nw")
        self.hamming_gosterge.bind("<Configure>",
            lambda e: hamming_tuval.configure(scrollregion=hamming_tuval.bbox("all")))

        # --- Parity adim adim gosterme butonu ---
        tk.Button(ust_cerceve,
                  text="PARITY HESABINI ADIM ADIM GOSTER",
                  font=("Consolas", 10, "bold"),
                  bg=self.renkler["vurgu"],
                  fg=self.renkler["sari"],
                  activebackground="#1a4a7a",
                  relief="flat", bd=0,
                  padx=10, pady=5,
                  cursor="hand2",
                  command=self.parity_adimlarini_goster).pack(pady=(4, 2))

        # --- Renk aciklamasi (legend) ---
        aciklama = tk.Frame(ust_cerceve, bg=self.renkler["panel"])
        aciklama.pack(pady=(2, 8))

        for renk, etiket in [(self.renkler["parity_arka"], "Parity Biti"),
                              (self.renkler["veri_arka"],  "Veri Biti")]:
            kare = tk.Frame(aciklama, bg=renk, width=14, height=14)
            kare.pack(side="left", padx=3)
            tk.Label(aciklama, text=etiket,
                     font=("Consolas", 8),
                     fg=self.renkler["alt_yazi"],
                     bg=self.renkler["panel"]).pack(side="left", padx=(0, 8))


    def bellek_paneli_kur(self, ust_cerceve):
        """
        Sag paneli doldurur:
        - Tıklanabilir bellek bitleri (hata olusturmak icin)
        - Sendrom hesapla butonu
        - Hatay duzelt butonu
        - Sonuc etiketi
        - Karsilastirma tablosu
        """

        tk.Label(ust_cerceve,
                 text="Bellek / Hata / Duzeltme",
                 font=("Consolas", 12, "bold"),
                 fg=self.renkler["sari"],
                 bg=self.renkler["panel"]).pack(pady=(12, 4))

        tk.Label(ust_cerceve,
                 text="Bellege yazilmis veri asagida.\n"
                      "Herhangi bir bite tikla -> o bit bozulur (yapay hata).",
                 font=("Consolas", 9),
                 fg=self.renkler["alt_yazi"],
                 bg=self.renkler["panel"],
                 justify="center").pack(pady=(0, 6))

        # --- Tıklanabilir bit alani (kaydirmali) ---
        bit_dis = tk.Frame(ust_cerceve, bg=self.renkler["panel"])
        bit_dis.pack(pady=4, padx=10, fill="x")

        bit_kaydirma = tk.Scrollbar(bit_dis, orient="horizontal")
        bit_kaydirma.pack(side="bottom", fill="x")

        bit_tuval = tk.Canvas(bit_dis, height=62,
                              bg=self.renkler["panel"],
                              highlightthickness=0,
                              xscrollcommand=bit_kaydirma.set)
        bit_tuval.pack(side="top", fill="x")
        bit_kaydirma.config(command=bit_tuval.xview)

        self.bit_alani = tk.Frame(bit_tuval, bg=self.renkler["panel"])
        bit_tuval.create_window((0, 0), window=self.bit_alani, anchor="nw")
        self.bit_alani.bind("<Configure>",
            lambda e: bit_tuval.configure(scrollregion=bit_tuval.bbox("all")))

        # --- Sendrom ve duzeltme butonlari ---
        buton_satiri = tk.Frame(ust_cerceve, bg=self.renkler["panel"])
        buton_satiri.pack(pady=8)

        tk.Button(buton_satiri,
                  text="SENDROMU HESAPLA",
                  font=("Consolas", 10, "bold"),
                  bg=self.renkler["sari"],
                  fg="#000000",
                  activebackground="#e0b050",
                  relief="flat", bd=0,
                  padx=8, pady=5,
                  cursor="hand2",
                  command=self.hata_tespit_et).pack(side="left", padx=4)

        tk.Button(buton_satiri,
                  text="HATAYI DUZELT",
                  font=("Consolas", 10, "bold"),
                  bg=self.renkler["hata_rengi"],
                  fg="#ffffff",
                  activebackground="#c73652",
                  relief="flat", bd=0,
                  padx=8, pady=5,
                  cursor="hand2",
                  command=self.hatayi_duzelt_ve_goster).pack(side="left", padx=4)

        # --- Sonuc kutusu ---
        sonuc_cerceve = tk.Frame(ust_cerceve,
                                  bg=self.renkler["vurgu"],
                                  relief="ridge", bd=2)
        sonuc_cerceve.pack(fill="x", padx=14, pady=6)

        tk.Label(sonuc_cerceve,
                 text="Sonuc:",
                 font=("Consolas", 10, "bold"),
                 fg=self.renkler["alt_yazi"],
                 bg=self.renkler["vurgu"]).pack(anchor="w", padx=8, pady=(6, 0))

        self.sonuc_etiketi = tk.Label(sonuc_cerceve,
                                       text="---",
                                       font=("Consolas", 12, "bold"),
                                       fg=self.renkler["yazi"],
                                       bg=self.renkler["vurgu"],
                                       wraplength=340,
                                       justify="left")
        self.sonuc_etiketi.pack(anchor="w", padx=8, pady=(0, 8))

        # --- Karsilastirma tablosu ---
        # Encode sonrasi veya duzeltme sonrasi orijinal vs kurtarilan veri
        tk.Label(ust_cerceve,
                 text="Veri Karsilastirmasi:",
                 font=("Consolas", 10),
                 fg=self.renkler["alt_yazi"],
                 bg=self.renkler["panel"]).pack(pady=(8, 2))

        self.karsilastirma_alani = tk.Frame(ust_cerceve, bg=self.renkler["panel"])
        self.karsilastirma_alani.pack(pady=2, padx=10)


    def log_alani_kur(self):
        """
        Ekranin en altina bir metin kutusu ekler.
        Yapilan her islem buraya kayit olarak yazilir.
        """
        log_cerceve = tk.Frame(self.pencere, bg=self.renkler["arkaplan"])
        log_cerceve.pack(fill="x", padx=20, pady=(4, 14))

        tk.Label(log_cerceve,
                 text="Islem Kayitlari",
                 font=("Consolas", 10, "bold"),
                 fg=self.renkler["alt_yazi"],
                 bg=self.renkler["arkaplan"]).pack(anchor="w")

        self.log_kutusu = tk.Text(log_cerceve,
                                   height=5,
                                   font=("Consolas", 9),
                                   bg=self.renkler["vurgu"],
                                   fg=self.renkler["yesil"],
                                   relief="flat", bd=4,
                                   state="disabled")   # kullanici yazamasin
        self.log_kutusu.pack(fill="x")


    # ============================================================
    #   YARDIMCI FONKSIYONLAR
    #   Kucuk, tekrar kullanilan islemler burada.
    # ============================================================

    def log_yaz(self, mesaj):
        """Log kutusuna bir satir yazar."""
        self.log_kutusu.configure(state="normal")      # once yazilabilir yap
        self.log_kutusu.insert("end", f"> {mesaj}\n")  # sona ekle
        self.log_kutusu.see("end")                     # en alta kaydir
        self.log_kutusu.configure(state="disabled")    # tekrar kilitle


    def girisi_dogrula(self, olay=None):
        """
        Kullanici giris kutusuna her karakter yazdiginda calisir.
        Sadece 0 ve 1 karakterlerine izin verir, digerlerini siler.
        Ayrica kac karakter girildigini gosterir.
        """
        girilenler = self.veri_girisi.get()
        beklenen_bit = self.bit_degiskeni.get()

        # Sadece 0 ve 1 iceren karakterleri filtrele
        temiz = ''.join(c for c in girilenler if c in '01')

        # Eger silinmesi gereken karakter varsa girisi guncelle
        if temiz != girilenler:
            self.veri_girisi.delete(0, "end")
            self.veri_girisi.insert(0, temiz)

        # Sayac etiketi guncelle (ornek: "5/8")
        self.uzunluk_etiketi.config(text=f"{len(temiz)}/{beklenen_bit}")


    def bit_degistiginde(self):
        """
        Kullanici bit boyutu secimini degistirdiginde calisir.
        Giris kutusunu temizler ve sayaci sifirlar.
        """
        self.veri_girisi.delete(0, "end")
        self.uzunluk_etiketi.config(text=f"0/{self.bit_degiskeni.get()}")


    def hamming_gostergeyi_temizle(self):
        """Hamming kodu gosterim alanindaki tum widget'lari siler."""
        for widget in self.hamming_gosterge.winfo_children():
            widget.destroy()


    def bit_alanini_temizle(self):
        """Bellek bit butonlarini temizler ve listeyi bosaltir."""
        for widget in self.bit_alani.winfo_children():
            widget.destroy()
        self.bit_butonlari = []


    def karsilastirmayi_temizle(self):
        """Karsilastirma tablosunu temizler."""
        for widget in self.karsilastirma_alani.winfo_children():
            widget.destroy()


    # ============================================================
    #   ANA ISLEM FONKSIYONLARI
    #   Butonlara basildiginda cagirilan ana fonksiyonlar.
    # ============================================================

    def encode_et(self):
        """
        'Encode Et ve Bellege Yaz' butonuna basildiginda calisir.

        1) Kullanicinin girisini kontrol eder
        2) hamming_encode() ile kodu olusturur
        3) Renkli kutularda gosterir
        4) Tıklanabilir bellek butonlarini olusturur
        """
        veri = self.veri_girisi.get().strip()
        beklenen_bit = self.bit_degiskeni.get()

        # Giris kontrolu: dogru uzunlukta mi?
        if len(veri) != beklenen_bit:
            messagebox.showerror("Hata",
                f"Lutfen tam olarak {beklenen_bit} bit girin!\n"
                f"Su an {len(veri)} bit girildi.")
            return

        # Giris kontrolu: sadece 0 ve 1 var mi?
        if not all(c in '01' for c in veri):
            messagebox.showerror("Hata", "Sadece 0 ve 1 giriniz!")
            return

        # Girisi kaydet
        self.orijinal_veri = veri

        # Hamming kodunu hesapla ve bellege yaz
        self.bellekteki_bitler = hamming_encode(veri)

        # Bilgi hesapla
        parity_sayisi = kac_parity_biti_gerekir(beklenen_bit)
        toplam_bit = beklenen_bit + parity_sayisi
        parity_pozlar = parity_pozisyonlarini_bul(toplam_bit)

        # Loga yaz
        self.log_yaz(f"Giris verisi ({beklenen_bit} bit): {veri}")
        self.log_yaz(f"Parity bit sayisi: {parity_sayisi}  |  Toplam bit: {toplam_bit}")
        self.log_yaz(f"Hamming kodu: {''.join(map(str, self.bellekteki_bitler))}")

        # --- Hamming kodu gostergesini olustur ---
        # Her bit icin renkli bir kutu ciziyor
        self.hamming_gostergeyi_temizle()
        for i, bit in enumerate(self.bellekteki_bitler):
            pozisyon = i + 1
            parity_mi = (pozisyon in parity_pozlar)

            # Parity bitleri mor, veri bitleri mavi
            arka_renk = self.renkler["parity_arka"] if parity_mi else self.renkler["veri_arka"]

            kutu = tk.Frame(self.hamming_gosterge, bg=arka_renk,
                             relief="solid", bd=1)
            kutu.pack(side="left", padx=1)

            # Ust kisimda pozisyon numarasi
            tk.Label(kutu, text=str(pozisyon),
                     font=("Consolas", 7),
                     fg=self.renkler["alt_yazi"],
                     bg=arka_renk).pack()

            # Alt kisimda bit degeri
            tk.Label(kutu, text=str(bit),
                     font=("Consolas", 12, "bold"),
                     fg=self.renkler["yesil"] if parity_mi else self.renkler["yazi"],
                     bg=arka_renk,
                     width=2).pack()

        # --- Tiklanabilir bellek butonlarini olustur ---
        self.bellek_bitlerini_olustur(parity_pozlar)

        # Karsilastirma tablosunu temizle (eski veri kalmasin)
        self.karsilastirmayi_temizle()

        self.sonuc_etiketi.config(
            text="Veri encode edildi ve bellege yazildi.",
            fg=self.renkler["yesil"])


    def bellek_bitlerini_olustur(self, parity_pozlar):
        """
        Bellekteki her bit icin tıklanabilir bir buton olusturur.
        Butona tıklamak o biti bozar (yapay hata).
        """
        self.bit_alanini_temizle()
        self.bit_butonlari = []

        # Pozisyon numaralarini gostermek icin ust satir
        pozisyon_satiri = tk.Frame(self.bit_alani, bg=self.renkler["panel"])
        pozisyon_satiri.pack()

        # Asıl bit butonlarinin oldugu alt satir
        buton_satiri = tk.Frame(self.bit_alani, bg=self.renkler["panel"])
        buton_satiri.pack()

        for i, bit in enumerate(self.bellekteki_bitler):
            pozisyon = i + 1
            parity_mi = (pozisyon in parity_pozlar)
            arka_renk = self.renkler["parity_arka"] if parity_mi else self.renkler["veri_arka"]

            # Pozisyon numarasi etiketi (ust satira)
            tk.Label(pozisyon_satiri,
                     text=str(pozisyon),
                     font=("Consolas", 7),
                     fg=self.renkler["alt_yazi"],
                     bg=self.renkler["panel"],
                     width=3).pack(side="left", padx=1)

            # Bit butonu cercevesi (alt satira)
            kutu = tk.Frame(buton_satiri, bg=arka_renk, relief="solid", bd=1)
            kutu.pack(side="left", padx=1, pady=1)

            # Tıklanabilir bit butonu
            # lambda idx=i: ... ile her buton kendi indeksini biliyor
            btn = tk.Button(kutu,
                            text=str(bit),
                            font=("Consolas", 11, "bold"),
                            bg=arka_renk,
                            fg=self.renkler["yazi"],
                            relief="flat", bd=0,
                            width=2, height=1,
                            cursor="hand2",
                            command=lambda idx=i: self.biti_boz(idx))
            btn.pack()
            self.bit_butonlari.append(btn)


    def biti_boz(self, indeks):
        """
        Kullanici bir bit butonuna tıkladiginda calisir.
        O bitin degerini tersine cevirir (0->1 veya 1->0).
        Bu, gercek hayatta iletim sirasinda olusan hatayi simule eder.
        """
        if not self.bellekteki_bitler:
            return

        # Biti tersine cevir
        self.bellekteki_bitler[indeks] ^= 1

        # Butonun gosterdigini guncelle
        buton = self.bit_butonlari[indeks]
        buton.config(text=str(self.bellekteki_bitler[indeks]))

        # Orijinal hamming kodu ile karsilastir
        # Eger farkli ise kirmizi yap, orijinaline donduyse rengi geri al
        orijinal_hamming = hamming_encode(self.orijinal_veri)
        if self.bellekteki_bitler[indeks] != orijinal_hamming[indeks]:
            buton.config(bg=self.renkler["hata_arka"], fg=self.renkler["hata_rengi"])
        else:
            # Orijinal degerine dondu -> rengi sifirla
            pozisyon = indeks + 1
            parity_pozlar = parity_pozisyonlarini_bul(len(self.bellekteki_bitler))
            arka = self.renkler["parity_arka"] if pozisyon in parity_pozlar else self.renkler["veri_arka"]
            buton.config(bg=arka, fg=self.renkler["yazi"])

        self.log_yaz(f"Bit {indeks+1} degistirildi -> yeni deger: {self.bellekteki_bitler[indeks]}")
        self.sonuc_etiketi.config(
            text="Bit bozuldu! Sendromu hesaplayin.",
            fg=self.renkler["sari"])


    def hata_tespit_et(self):
        """
        'Sendromu Hesapla' butonuna basildiginda calisir.

        Sendrom = tum parity bitlerinin XOR kontrolunun sonucu.
        Sendrom 0 ise hata yok.
        Sendrom != 0 ise o pozisyonda hata var.
        Birden fazla bit bozuksa uyari verir (Hamming sadece 1 biti duzeltebilir).
        """
        if not self.bellekteki_bitler:
            messagebox.showwarning("Uyari", "Once veri encode edin!")
            return

        # Kac bit bozuldu? (orijinal ile karsilastir)
        orijinal_hamming = hamming_encode(self.orijinal_veri)
        hata_sayisi = sum(1 for a, b in zip(self.bellekteki_bitler, orijinal_hamming) if a != b)

        # Sendromu hesapla
        sendrom = sendrom_hesapla(self.bellekteki_bitler)
        self.log_yaz(f"Sendrom degeri: {sendrom}")

        # Coklu hata kontrolu
        if hata_sayisi >= 2:
            self.sonuc_etiketi.config(
                text=f"COKLU HATA! ({hata_sayisi} bit bozuk)\n"
                     f"Hamming kodu yalnizca TEK bit hatasini duzeltebilir!\n"
                     f"Sendrom = {sendrom} ama bu degere guvenilemez.",
                fg=self.renkler["hata_rengi"])
            self.log_yaz(f"UYARI: {hata_sayisi} bit bozulmus -> duzeltilemiyor!")
            return

        if sendrom == 0:
            self.sonuc_etiketi.config(
                text="Sendrom = 0  ->  Hata YOK! Veri saglikli.",
                fg=self.renkler["yesil"])
            self.log_yaz("Sonuc: Hata tespit edilmedi.")
        else:
            self.sonuc_etiketi.config(
                text=f"Sendrom = {sendrom}  ->  Bit {sendrom} hatali!\n"
                     f"(Pozisyon {sendrom} duzeltilmeyi bekliyor)",
                fg=self.renkler["hata_rengi"])
            self.log_yaz(f"Sonuc: Pozisyon {sendrom} hatali tespit edildi!")

            # Hatali butonu kirmizi yap
            if 0 < sendrom <= len(self.bit_butonlari):
                self.bit_butonlari[sendrom - 1].config(bg=self.renkler["hata_arka"])


    def hatayi_duzelt_ve_goster(self):
        """
        'Hatayi Duzelt' butonuna basildiginda calisir.

        1) Sendromu hesapla
        2) Sendromun gosterdigi pozisyondaki biti duzelt
        3) Parity bitlerini atarak orijinal veriyi kurtar
        4) Orijinal veri ile karsilastir
        """
        if not self.bellekteki_bitler:
            messagebox.showwarning("Uyari", "Once veri encode edin!")
            return

        # Coklu hata varsa duzeltme yapma
        orijinal_hamming = hamming_encode(self.orijinal_veri)
        hata_sayisi = sum(1 for a, b in zip(self.bellekteki_bitler, orijinal_hamming) if a != b)

        if hata_sayisi >= 2:
            messagebox.showerror("Duzeltilemiyor",
                f"{hata_sayisi} bit bozuk!\n"
                "Hamming kodu sadece tek bit hatasini duzeltebilir.")
            return

        sendrom = sendrom_hesapla(self.bellekteki_bitler)

        if sendrom == 0:
            self.sonuc_etiketi.config(
                text="Duzeltilecek hata yok, veri temiz!",
                fg=self.renkler["yesil"])
            return

        # Hatali biti duzelt
        self.bellekteki_bitler = hatayi_duzelt(self.bellekteki_bitler, sendrom)

        # Buton gostergesini guncelle
        duzeltilen_buton = self.bit_butonlari[sendrom - 1]
        duzeltilen_buton.config(text=str(self.bellekteki_bitler[sendrom - 1]))

        # Rengi normale dondur
        pozisyon = sendrom
        parity_pozlar = parity_pozisyonlarini_bul(len(self.bellekteki_bitler))
        arka = self.renkler["parity_arka"] if pozisyon in parity_pozlar else self.renkler["veri_arka"]
        duzeltilen_buton.config(bg=arka, fg=self.renkler["yazi"])

        self.log_yaz(f"Pozisyon {sendrom} duzeltildi -> bit {self.bellekteki_bitler[sendrom-1]} yapildi")

        # --- Parity bitlerini atarak orijinal veriyi kurtar ---
        # Sadece parity olmayan pozisyonlardaki bitler gercek veri
        toplam = len(self.bellekteki_bitler)
        parity_pozlar = parity_pozisyonlarini_bul(toplam)
        kurtarilan_bitler = [
            str(self.bellekteki_bitler[i])
            for i in range(toplam)
            if (i + 1) not in parity_pozlar  # parity pozisyonu degilse al
        ]
        kurtarilan_veri = ''.join(kurtarilan_bitler)

        eslesti_mi = 'EVET' if kurtarilan_veri == self.orijinal_veri else 'HAYIR'

        self.sonuc_etiketi.config(
            text=f"Hata duzeltildi!\n"
                 f"Orijinal veri  : {self.orijinal_veri}\n"
                 f"Kurtarilan     : {kurtarilan_veri}\n"
                 f"Eslesme        : {eslesti_mi}",
            fg=self.renkler["yesil"])

        # Karsilastirma tablosunu goster
        self.karsilastirma_goster(self.orijinal_veri, kurtarilan_veri)


    def karsilastirma_goster(self, orijinal, kurtarilan):
        """
        Orijinal veri ile kurtarilan veriyi yan yana tablo olarak gosterir.
        Eslesen bitler yesil, farkli bitler kirmizi gosterilir.
        """
        self.karsilastirmayi_temizle()

        # Tablo basliklari
        for sutun, baslik in enumerate(["", "Veri"]):
            tk.Label(self.karsilastirma_alani,
                     text=baslik,
                     font=("Consolas", 9, "bold"),
                     fg=self.renkler["sari"],
                     bg=self.renkler["panel"]).grid(row=0, column=sutun, padx=4, pady=2)

        # Tablo satirlari
        for satir_no, (etiket, veri) in enumerate([("Orijinal", orijinal),
                                                    ("Kurtarilan", kurtarilan)],
                                                   start=1):
            tk.Label(self.karsilastirma_alani,
                     text=etiket,
                     font=("Consolas", 9),
                     fg=self.renkler["alt_yazi"],
                     bg=self.renkler["panel"]).grid(row=satir_no, column=0, padx=4, pady=1)

            # Bitleri tek tek goster, yesil=eslesir, kirmizi=farkli
            bit_satiri = tk.Frame(self.karsilastirma_alani, bg=self.renkler["panel"])
            bit_satiri.grid(row=satir_no, column=1, padx=4, pady=1)

            for i, bit in enumerate(veri):
                esleşiyor = (len(orijinal) > i and orijinal[i] == bit)
                renk = self.renkler["yesil"] if esleşiyor else self.renkler["hata_rengi"]
                tk.Label(bit_satiri,
                         text=bit,
                         font=("Consolas", 10, "bold"),
                         fg=renk,
                         bg=self.renkler["panel"]).pack(side="left", padx=1)


    # ============================================================
    #   PARITY ADIM ADIM PENCERESI
    #   Her parity bitinin nasil hesaplandigi burada gosterilir.
    # ============================================================

    def parity_adimlarini_goster(self):
        """
        Ayri bir pencere acar ve her parity bitinin hesaplanma adimlarini
        XOR zincirleri ile gosterir.

        Ornek cikti:
          P1 -> Pozisyon 1 (2^0) Parity Biti
          Hangi bitlere bakiyor? [1]=0  [3]=1  [5]=0  ...
          XOR zinciri: 0 xor 1 xor 0 = 1
          P1 = 1 -> Bu parity biti HATALI
        """
        if not self.bellekteki_bitler:
            messagebox.showwarning("Uyari", "Once veri encode edin!")
            return

        toplam = len(self.bellekteki_bitler)
        parity_sayisi = kac_parity_biti_gerekir(len(self.orijinal_veri))

        # --- Yeni pencere olustur ---
        pencere = tk.Toplevel(self.pencere)
        pencere.title("Parity Bit Hesaplama Adimlari")
        pencere.geometry("620x500")
        pencere.configure(bg=self.renkler["arkaplan"])

        tk.Label(pencere,
                 text="Parity Bit Hesaplama Adimlari",
                 font=("Consolas", 13, "bold"),
                 fg=self.renkler["sari"],
                 bg=self.renkler["arkaplan"]).pack(pady=(14, 4))

        tk.Label(pencere,
                 text=f"Hamming kodu: {''.join(map(str, self.bellekteki_bitler))}   "
                      f"(toplam {toplam} bit, {parity_sayisi} parity biti)",
                 font=("Consolas", 10),
                 fg=self.renkler["alt_yazi"],
                 bg=self.renkler["arkaplan"]).pack(pady=(0, 8))

        # Kaydirmali metin alani
        cerceve = tk.Frame(pencere, bg=self.renkler["arkaplan"])
        cerceve.pack(fill="both", expand=True, padx=16, pady=4)

        kaydirma = tk.Scrollbar(cerceve)
        kaydirma.pack(side="right", fill="y")

        metin = tk.Text(cerceve,
                        font=("Consolas", 10),
                        bg=self.renkler["vurgu"],
                        fg=self.renkler["yazi"],
                        relief="flat", bd=4,
                        yscrollcommand=kaydirma.set)
        metin.pack(fill="both", expand=True)
        kaydirma.config(command=metin.yview)

        # Her parity biti icin adim adim hesaplama yaz
        for i in range(parity_sayisi):
            parity_pos = 2 ** i  # 1, 2, 4, 8, ...

            metin.insert("end", f"{'='*50}\n", "baslik")
            metin.insert("end", f"  P{parity_pos}  ->  Pozisyon {parity_pos} (2^{i}) Parity Biti\n", "parity")
            metin.insert("end", f"{'='*50}\n", "baslik")
            metin.insert("end", f"  Hangi bitlere bakiyor? (pozisyon AND {parity_pos} != 0 olanlar)\n\n", "bilgi")

            # Bu parity bitinin sorumlu oldugu pozisyonlar
            sorumlu_pozlar = [k for k in range(1, toplam + 1) if k & parity_pos]

            # Pozisyon ve degerleri listele
            satir = "  Pozisyonlar: "
            for k in sorumlu_pozlar:
                satir += f"[{k}]={self.bellekteki_bitler[k-1]}  "
            metin.insert("end", satir + "\n\n", "bitler")

            # XOR zinciri hesapla ve yaz
            xor_satir = "  XOR zinciri: "
            sonuc = 0
            for k in sorumlu_pozlar:
                sonuc ^= self.bellekteki_bitler[k - 1]
                xor_satir += str(self.bellekteki_bitler[k-1])
                if k != sorumlu_pozlar[-1]:
                    xor_satir += " xor "
            xor_satir += f" = {sonuc}"
            metin.insert("end", xor_satir + "\n\n", "xor")

            # Sonuc: dogru mu yoksa hatali mi?
            if sonuc == 0:
                metin.insert("end", f"  TAMAM  P{parity_pos} = {sonuc}  -> Parity biti DOGRU\n\n", "tamam")
            else:
                metin.insert("end", f"  HATA   P{parity_pos} = {sonuc}  -> Parity biti HATALI\n\n", "hata")

        # Genel sendrom sonucu
        sendrom = sendrom_hesapla(self.bellekteki_bitler)
        metin.insert("end", f"{'='*50}\n", "baslik")
        metin.insert("end", f"  SENDROM SONUCU = {sendrom}\n", "parity")
        if sendrom == 0:
            metin.insert("end", "  -> Hata yok!\n", "tamam")
        else:
            metin.insert("end", f"  -> Hatali bit pozisyonu: {sendrom}\n", "hata")
        metin.insert("end", f"{'='*50}\n", "baslik")

        # Renk tagimlari
        metin.tag_config("baslik",  foreground=self.renkler["alt_yazi"])
        metin.tag_config("parity",  foreground=self.renkler["sari"],
                         font=("Consolas", 10, "bold"))
        metin.tag_config("bilgi",   foreground=self.renkler["alt_yazi"])
        metin.tag_config("bitler",  foreground=self.renkler["yazi"])
        metin.tag_config("xor",     foreground=self.renkler["yesil"])
        metin.tag_config("tamam",   foreground=self.renkler["yesil"])
        metin.tag_config("hata",    foreground=self.renkler["hata_rengi"])
        metin.configure(state="disabled")  # kullanici degistiremesin


# ============================================================
#   PROGRAMI BASLAT
#   Bu dosya dogrudan calistirilirsa buradan baslar.
# ============================================================

if __name__ == "__main__":
    ana_pencere = tk.Tk()
    uygulama = HammingSimulatoru(ana_pencere)
    ana_pencere.mainloop()   # pencere kapanana kadar calis