import tkinter as tk
from tkinter import messagebox


# --- yardimci hesaplamalar ---

def kacParityBit(veriLen):
    # 2^r >=n + r + 1 saglana kadar arttir
    r = 0
    while (2 ** r) < (veriLen + r + 1):
        r += 1
    return r


def parityPozlari(toplamLen):
    # 1, 2, 4, 8... seklinde 2 kuvvetleri
    pozlar = []
    i = 1
    while i <= toplamLen:
        pozlar.append(i)
        i *= 2
    return pozlar


def hammingEncode(veriBitleri):
    veriLen = len(veriBitleri)
    parSay = kacParityBit(veriLen)
    toplamLen = veriLen + parSay

    dizi = [0] * (toplamLen + 1)

    # once veri bitlerini yerlestir, parity pozlari bos kalsin
    vIdx = 0
    for pos in range(1, toplamLen + 1):
        if pos & (pos - 1) != 0:  # 2 kuvveti degilse veri gidecektir
            dizi[pos] = int(veriBitleri[vIdx])
            vIdx += 1

    # sonra her parity bitini tek tek hesaplarız
    for i in range(parSay):
        pPos = 2 ** i
        xr = 0
        for k in range(1, toplamLen + 1):
            if k & pPos:
                xr ^= dizi[k]
        dizi[pPos] = xr
    return dizi[1:]


def sendromHesapla(bitler):
    n = len(bitler)
    r = 0
    while (2 ** r) < n + 1:
        r += 1

    sendrom = 0
    for i in range(r):
        pPos = 2 ** i
        xr = 0
        for k in range(1, n + 1):
            if k & pPos:
                xr ^= bitler[k - 1]
        if xr != 0:
            sendrom += pPos

    return sendrom


def bitDuzelt(bitler, pos):
    kopyа = bitler[:]
    if 0 < pos <= len(kopyа):
        kopyа[pos - 1] ^= 1
    return kopyа


# ------------------------------------------------------------------------------------------------------

class HammingSimulatoru:

    def __init__(self, pencere):
        self.pencere = pencere
        self.pencere.title("Hamming Hata duzeltme Simulatoru")
        self.pencere.geometry("950x750")
        self.pencere.configure(bg="#1a1a2e")
        self.pencere.resizable(True,True)

        self.renkler = {
            "arkaplan":    "#1a1a2e",
            "panel":       "#16213e",
            "vurgu":       "#0f3460",
            "hataRengi":   "#e94560",
            "yesil":       "#00b894",
            "sari":        "#fdcb6e",
            "yazi":        "#eaeaea",
            "altYazi":     "#a0a0b0",
            "parityArka":  "#2d1b4e",
            "veriArka":    "#1b3a4e",
            "hataArka":    "#4e1b1b",
        }

        self.bellekBitler = []
        self.orijinalVeri = ""
        self.bitButonlari = []

        self.arayuzKur()

    # arayuzumuz

    def arayuzKur(self):
        baslikF = tk.Frame(self.pencere, bg=self.renkler["arkaplan"])
        baslikF.pack(fill="x", padx=20, pady=(15, 5))

        tk.Label(baslikF,
                 text="Hamming Kodu Simulatoru",
                 font=("Consolas", 18, "bold"),
                 fg=self.renkler["hataRengi"],
                 bg=self.renkler["arkaplan"]).pack()

        tk.Label(baslikF,
                 text="Bilgisayar Mimarisi",
                 font=("Consolas", 10),
                 fg=self.renkler["altYazi"],
                 bg=self.renkler["arkaplan"]).pack()

        ortaF = tk.Frame(self.pencere, bg=self.renkler["arkaplan"])
        ortaF.pack(fill="both", expand=True, padx=20, pady=5)

        solPanel = tk.Frame(ortaF, bg=self.renkler["panel"], relief="ridge", bd=2)
        solPanel.pack(side="left", fill="both", expand=True, padx=(0, 8))

        sagPanel = tk.Frame(ortaF, bg=self.renkler["panel"], relief="ridge", bd=2)
        sagPanel.pack(side="left", fill="both", expand=True)

        self.girisPanel(solPanel)
        self.bellekPanel(sagPanel)
        self.logAlaniKur()

    def girisPanel(self, f):
        tk.Label(f, text="Veri Girisi ve Encode",
                 font=("Consolas", 12, "bold"),
                 fg=self.renkler["yesil"],
                 bg=self.renkler["panel"]).pack(pady=(12, 4))

        bitSecF = tk.Frame(f, bg=self.renkler["panel"])
        bitSecF.pack(pady=4)

        tk.Label(bitSecF, text="Bit Boyutu:",
                 font=("Consolas", 10),
                 fg=self.renkler["yazi"],
                 bg=self.renkler["panel"]).pack(side="left", padx=4)

        self.bitDeg = tk.IntVar(value=8)

        for deger in [8, 16, 32]:
            tk.Radiobutton(bitSecF, text=f"{deger} bit",
                           variable=self.bitDeg, value=deger,
                           font=("Consolas", 10),
                           fg=self.renkler["yazi"],
                           bg=self.renkler["panel"],
                           selectcolor=self.renkler["vurgu"],
                           activebackground=self.renkler["panel"],
                           command=self.bitDegisti).pack(side="left", padx=6)

        tk.Label(f, text="ikili Veri Giriniz:",
                 font=("Consolas", 10),
                 fg=self.renkler["altYazi"],
                 bg=self.renkler["panel"]).pack(pady=(8, 2))

        girisS = tk.Frame(f, bg=self.renkler["panel"])
        girisS.pack(pady=2)

        self.veriGirisi = tk.Entry(girisS, width=36,
                                    font=("Consolas", 13),
                                    bg=self.renkler["vurgu"],
                                    fg=self.renkler["yesil"],
                                    insertbackground=self.renkler["yesil"],
                                    relief="flat", bd=4)
        self.veriGirisi.pack(side="left", padx=4)
        self.veriGirisi.bind("<KeyRelease>", self.girisDogrula)

        self.uzunlukEtik = tk.Label(girisS, text="0/8",
                                     font=("Consolas", 10),
                                     fg=self.renkler["altYazi"],
                                     bg=self.renkler["panel"])
        self.uzunlukEtik.pack(side="left")

        tk.Button(f, text="ENCODE ET ve BELLEGE YAZ",
                  font=("Consolas", 11, "bold"),
                  bg=self.renkler["yesil"], fg="#000000",
                  activebackground="#00a381",
                  relief="flat", bd=0, padx=12, pady=6,
                  cursor="hand2",
                  command=self.encodeEt).pack(pady=10)

        tk.Label(f, text="Hamming Kodu(Bellege Yazidigimiz):",
                 font=("Consolas", 10),
                 fg=self.renkler["altYazi"],
                 bg=self.renkler["panel"]).pack(pady=(6, 2))

        hDis = tk.Frame(f, bg=self.renkler["panel"])
        hDis.pack(pady=4, padx=10, fill="x")

        hKay = tk.Scrollbar(hDis, orient="horizontal")
        hKay.pack(side="bottom", fill="x")

        hTuval = tk.Canvas(hDis, height=52,
                            bg=self.renkler["panel"],
                            highlightthickness=0,
                            xscrollcommand=hKay.set)
        hTuval.pack(side="top", fill="x")
        hKay.config(command=hTuval.xview)

        self.hammingGosterge = tk.Frame(hTuval, bg=self.renkler["panel"])
        hTuval.create_window((0, 0), window=self.hammingGosterge, anchor="nw")
        self.hammingGosterge.bind("<Configure>",
            lambda e: hTuval.configure(scrollregion=hTuval.bbox("all")))

        tk.Button(f, text="PARITY HESABI Basit Adimlar",
                  font=("Consolas", 10, "bold"),
                  bg=self.renkler["vurgu"],
                  fg=self.renkler["sari"],
                  activebackground="#1a4a7a",
                  relief="flat", bd=0, padx=10, pady=5,
                  cursor="hand2",
                  command=self.parityAdimGoster).pack(pady=(4, 2))

        aciklamaF = tk.Frame(f, bg=self.renkler["panel"])
        aciklamaF.pack(pady=(2, 8))
        for renk, etiket in [(self.renkler["parityArka"], "Parity Biti"),
                              (self.renkler["veriArka"],  "Veri Biti")]:
            tk.Frame(aciklamaF, bg=renk, width=14, height=14).pack(side="left", padx=3)
            tk.Label(aciklamaF, text=etiket,
                     font=("Consolas", 8),
                     fg=self.renkler["altYazi"],
                     bg=self.renkler["panel"]).pack(side="left", padx=(0, 8))

    def bellekPanel(self, f):
        tk.Label(f, text="Bellek / Hata / Duzeltme",
                 font=("Consolas", 12, "bold"),
                 fg=self.renkler["sari"],
                 bg=self.renkler["panel"]).pack(pady=(12, 4))

        tk.Label(f,
                 text="Bellege yazilmis veri su sekilde:\n"
                      "Herhangi bir bite tikla -> o bit bozulur (yapay hata)",
                 font=("Consolas", 9),
                 fg=self.renkler["altYazi"],
                 bg=self.renkler["panel"],
                 justify="center").pack(pady=(0, 6))

        bitDis = tk.Frame(f, bg=self.renkler["panel"])
        bitDis.pack(pady=4, padx=10, fill="x")

        bitKay = tk.Scrollbar(bitDis, orient="horizontal")
        bitKay.pack(side="bottom", fill="x")

        bitTuval = tk.Canvas(bitDis, height=62,
                              bg=self.renkler["panel"],
                              highlightthickness=0,
                              xscrollcommand=bitKay.set)
        bitTuval.pack(side="top", fill="x")
        bitKay.config(command=bitTuval.xview)

        self.bitAlani = tk.Frame(bitTuval, bg=self.renkler["panel"])
        bitTuval.create_window((0, 0), window=self.bitAlani, anchor="nw")
        self.bitAlani.bind("<Configure>",
            lambda e: bitTuval.configure(scrollregion=bitTuval.bbox("all")))

        butonS = tk.Frame(f, bg=self.renkler["panel"])
        butonS.pack(pady=8)

        tk.Button(butonS, text="SENDROMU HESAPLA",
                  font=("Consolas", 10, "bold"),
                  bg=self.renkler["sari"], fg="#000000",
                  activebackground="#e0b050",
                  relief="flat", bd=0, padx=8, pady=5,
                  cursor="hand2",
                  command=self.hataTespitEt).pack(side="left", padx=4)

        tk.Button(butonS, text="HATAYI DUZELT",
                  font=("Consolas", 10, "bold"),
                  bg=self.renkler["hataRengi"], fg="#ffffff",
                  activebackground="#c73652",
                  relief="flat", bd=0, padx=8, pady=5,
                  cursor="hand2",
                  command=self.hatayiDuzeltveGoster).pack(side="left", padx=4)

        sonucF = tk.Frame(f, bg=self.renkler["vurgu"], relief="ridge", bd=2)
        sonucF.pack(fill="x", padx=14, pady=6)

        tk.Label(sonucF, text="Sonuc:",
                 font=("Consolas", 10, "bold"),
                 fg=self.renkler["altYazi"],
                 bg=self.renkler["vurgu"]).pack(anchor="w", padx=8, pady=(6, 0))

        self.sonucEtik = tk.Label(sonucF, text="-----",
                                   font=("Consolas", 12, "bold"),
                                   fg=self.renkler["yazi"],
                                   bg=self.renkler["vurgu"],
                                   wraplength=340, justify="left")
        self.sonucEtik.pack(anchor="w", padx=8, pady=(0, 8))

        tk.Label(f, text="Veri Karsilastirmasi:",
                 font=("Consolas", 10),
                 fg=self.renkler["altYazi"],
                 bg=self.renkler["panel"]).pack(pady=(8, 2))

        self.karsilastirmaAlani = tk.Frame(f, bg=self.renkler["panel"])
        self.karsilastirmaAlani.pack(pady=2, padx=10)

    def logAlaniKur(self):
        logF = tk.Frame(self.pencere, bg=self.renkler["arkaplan"])
        logF.pack(fill="x", padx=20, pady=(4, 14))

        tk.Label(logF, text="Islem Kayitlari",
                 font=("Consolas", 10, "bold"),
                 fg=self.renkler["altYazi"],
                 bg=self.renkler["arkaplan"]).pack(anchor="w")

        self.logKutu = tk.Text(logF, height=5,
                                font=("Consolas", 9),
                                bg=self.renkler["vurgu"],
                                fg=self.renkler["yesil"],
                                relief="flat", bd=4,
                                state="disabled")
        self.logKutu.pack(fill="x")

    # yardımci fonksiyonler

    def logYaz(self, msg):
        self.logKutu.configure(state="normal")
        self.logKutu.insert("end", f"> {msg}\n")
        self.logKutu.see("end")
        self.logKutu.configure(state="disabled")

    def girisDogrula(self, e=None):
        raw = self.veriGirisi.get()
        temiz = ''.join(c for c in raw if c in '01')
        if temiz != raw:
            self.veriGirisi.delete(0, "end")
            self.veriGirisi.insert(0, temiz)
        self.uzunlukEtik.config(text=f"{len(temiz)}/{self.bitDeg.get()}")

    def bitDegisti(self):
        self.veriGirisi.delete(0, "end")
        self.uzunlukEtik.config(text=f"0/{self.bitDeg.get()}")

    def hammingGostergeSifirla(self):
        for w in self.hammingGosterge.winfo_children():
            w.destroy()

    def bitAlaniSifirla(self):
        for w in self.bitAlani.winfo_children():
            w.destroy()
        self.bitButonlari = []

    def karsilastirmaSifirla(self):
        for w in self.karsilastirmaAlani.winfo_children():
            w.destroy()

    # ana hesaplama

    def encodeEt(self):
        veri = self.veriGirisi.get().strip()
        beklenen = self.bitDeg.get()

        if len(veri) != beklenen:
            messagebox.showerror("Hata",
                f" sectiginiz kadar {beklenen} bit girin\nSu an {len(veri)} bit var")
            return
        if not all(c in '01' for c in veri):
            messagebox.showerror("Hata", "veriler sadece 0 ve 1 ile yazilabilir")
            return

        self.orijinalVeri = veri
        self.bellekBitler = hammingEncode(veri)

        parSay = kacParityBit(beklenen)
        toplamBit = beklenen + parSay
        pPozlar = parityPozlari(toplamBit)

        self.logYaz(f"Giris ({beklenen} bit): {veri}")
        self.logYaz(f"Parity: {parSay}  |  Toplam: {toplamBit}")
        self.logYaz(f"Hamming: {''.join(map(str, self.bellekBitler))}")

        self.hammingGostergeSifirla()
        for i, bit in enumerate(self.bellekBitler):
            pos = i + 1
            parityMi = pos in pPozlar
            arka = self.renkler["parityArka"] if parityMi else self.renkler["veriArka"]
            kutu = tk.Frame(self.hammingGosterge, bg=arka, relief="solid", bd=1)
            kutu.pack(side="left", padx=1)
            tk.Label(kutu, text=str(pos),
                     font=("Consolas", 7), fg=self.renkler["altYazi"], bg=arka).pack()
            tk.Label(kutu, text=str(bit),
                     font=("Consolas", 12, "bold"),
                     fg=self.renkler["yesil"] if parityMi else self.renkler["yazi"],
                     bg=arka, width=2).pack()

        self.bellekButonOlustur(pPozlar)
        self.karsilastirmaSifirla()
        self.sonucEtik.config(text="Veri encode edildi ve bellege yazidim",
                               fg=self.renkler["yesil"])

    def bellekButonOlustur(self, pPozlar):
        self.bitAlaniSifirla()
        self.bitButonlari = []

        posSatir = tk.Frame(self.bitAlani, bg=self.renkler["panel"])
        posSatir.pack()
        btnSatir = tk.Frame(self.bitAlani, bg=self.renkler["panel"])
        btnSatir.pack()

        for i, bit in enumerate(self.bellekBitler):
            pos = i + 1
            parityMi = pos in pPozlar
            arka = self.renkler["parityArka"] if parityMi else self.renkler["veriArka"]

            tk.Label(posSatir, text=str(pos),
                     font=("Consolas", 7), fg=self.renkler["altYazi"],
                     bg=self.renkler["panel"], width=3).pack(side="left", padx=1)

            kutu = tk.Frame(btnSatir, bg=arka, relief="solid", bd=1)
            kutu.pack(side="left", padx=1, pady=1)

            btn = tk.Button(kutu, text=str(bit),
                            font=("Consolas", 11, "bold"),
                            bg=arka, fg=self.renkler["yazi"],
                            relief="flat", bd=0, width=2, height=1,
                            cursor="hand2",
                            command=lambda idx=i: self.bitiBoz(idx))
            btn.pack()
            self.bitButonlari.append(btn)

    def bitiBoz(self, idx):
        if not self.bellekBitler:
            return
        self.bellekBitler[idx] ^= 1

        btn = self.bitButonlari[idx]
        btn.config(text=str(self.bellekBitler[idx]))

        oriHamming = hammingEncode(self.orijinalVeri)
        if self.bellekBitler[idx] != oriHamming[idx]:
            btn.config(bg=self.renkler["hataArka"], fg=self.renkler["hataRengi"])
        else:
            pos = idx + 1
            pPozlar = parityPozlari(len(self.bellekBitler))
            arka = self.renkler["parityArka"] if pos in pPozlar else self.renkler["veriArka"]
            btn.config(bg=arka, fg=self.renkler["yazi"])

        self.logYaz(f"Bit {idx+1} degistirildi -> {self.bellekBitler[idx]}")
        self.sonucEtik.config(text="Bit bozuldu! Sendromu hesaplayin.",
                               fg=self.renkler["sari"])

    def hataTespitEt(self):
        if not self.bellekBitler:
            messagebox.showwarning("Uyari", "Once veri encode edin!")
            return

        oriHamming = hammingEncode(self.orijinalVeri)
        hataSay = sum(1 for a, b in zip(self.bellekBitler, oriHamming) if a != b)
        sendrom = sendromHesapla(self.bellekBitler)
        self.logYaz(f"Sendrom: {sendrom}")

        if hataSay >= 2:
            self.sonucEtik.config(
                text=f"COKLU HATA! ({hataSay} bit bozuk)\n"
                     f"Hamming sadece tek bit hatasini duzeltebilir\n"
                     f"Sendrom = {sendrom} ama guvenilmez.",
                fg=self.renkler["hataRengi"])
            self.logYaz(f"UYARI: {hataSay} bit bozulmus -> duzeltilemiyor!")
            return

        if sendrom == 0:
            self.sonucEtik.config(text="Sendrom = 0  ->  Hata yok.",
                                   fg=self.renkler["yesil"])
            self.logYaz("Hata tespit edilmedi.")
        else:
            self.sonucEtik.config(
                text=f"Sendrom = {sendrom}  ->  Bit {sendrom} hatali!",
                fg=self.renkler["hataRengi"])
            self.logYaz(f"Pozisyon {sendrom} hatali!")
            if 0 < sendrom <= len(self.bitButonlari):
                self.bitButonlari[sendrom - 1].config(bg=self.renkler["hataArka"])

    def hatayiDuzeltveGoster(self):
        if not self.bellekBitler:
            messagebox.showwarning("Uyari", "Once veri encode edin!")
            return

        oriHamming = hammingEncode(self.orijinalVeri)
        hataSay = sum(1 for a, b in zip(self.bellekBitler, oriHamming) if a != b)

        if hataSay >= 2:
            messagebox.showerror("Duzeltilemiyor",
                f"{hataSay} bit bozuk! Sadece tek bit duzeltebilirim.")
            return

        sendrom = sendromHesapla(self.bellekBitler)
        if sendrom == 0:
            self.sonucEtik.config(text="hata yok neyi duzeltelim?",
                                   fg=self.renkler["yesil"])
            return

        self.bellekBitler = bitDuzelt(self.bellekBitler, sendrom)

        duzBtn = self.bitButonlari[sendrom - 1]
        duzBtn.config(text=str(self.bellekBitler[sendrom - 1]))

        pos = sendrom
        pPozlar = parityPozlari(len(self.bellekBitler))
        arka = self.renkler["parityArka"] if pos in pPozlar else self.renkler["veriArka"]
        duzBtn.config(bg=arka, fg=self.renkler["yazi"])

        self.logYaz(f"Pozisyonu {sendrom} duzeltildi -> {self.bellekBitler[sendrom-1]}")

        # parity bitleri cikar, sadece veri kalsin
        n = len(self.bellekBitler)
        pPozlar = parityPozlari(n)
        kurtarilan = ''.join(
            str(self.bellekBitler[i])
            for i in range(n)
            if (i + 1) not in pPozlar
        )

        eslesti = 'EVET' if kurtarilan == self.orijinalVeri else 'HAYIR'
        self.sonucEtik.config(
            text=f"Hatayi duzelttik\n"
                 f"Orijinal   : {self.orijinalVeri}\n"
                 f"Kurtarilan : {kurtarilan}\n"
                 f"Eslesme    : {eslesti}",
            fg=self.renkler["yesil"])

        self.karsilastirmaGoster(self.orijinalVeri, kurtarilan)

    def karsilastirmaGoster(self, orijinal, kurtarilan):
        self.karsilastirmaSifirla()

        for sutun, baslik in enumerate(["", "Veri"]):
            tk.Label(self.karsilastirmaAlani, text=baslik,
                     font=("Consolas", 9, "bold"),
                     fg=self.renkler["sari"],
                     bg=self.renkler["panel"]).grid(row=0, column=sutun, padx=4, pady=2)

        for satirNo, (etiket, veri) in enumerate(
                [("Orijinal", orijinal), ("Kurtarilan", kurtarilan)], start=1):
            tk.Label(self.karsilastirmaAlani, text=etiket,
                     font=("Consolas", 9),
                     fg=self.renkler["altYazi"],
                     bg=self.renkler["panel"]).grid(row=satirNo, column=0, padx=4, pady=1)

            bitS = tk.Frame(self.karsilastirmaAlani, bg=self.renkler["panel"])
            bitS.grid(row=satirNo, column=1, padx=4, pady=1)

            for i, bit in enumerate(veri):
                eslesMi = len(orijinal) > i and orijinal[i] == bit
                renk = self.renkler["yesil"] if eslesMi else self.renkler["hataRengi"]
                tk.Label(bitS, text=bit,
                         font=("Consolas", 10, "bold"),
                         fg=renk, bg=self.renkler["panel"]).pack(side="left", padx=1)

    # parity penceremiz

    def parityAdimGoster(self):
        if not self.bellekBitler:
            messagebox.showwarning("Uyari", "Once veri encode edin!")
            return

        n = len(self.bellekBitler)
        parSay = kacParityBit(len(self.orijinalVeri))

        pop = tk.Toplevel(self.pencere)
        pop.title("Parity Bit Hesaplama Adimlari")
        pop.geometry("620x500")
        pop.configure(bg=self.renkler["arkaplan"])

        tk.Label(pop, text="Parity Bit Hesaplama Adimlari",
                 font=("Consolas", 13, "bold"),
                 fg=self.renkler["sari"],
                 bg=self.renkler["arkaplan"]).pack(pady=(14, 4))

        tk.Label(pop,
                 text=f"{''.join(map(str, self.bellekBitler))}   "
                      f"({n} bit, {parSay} parity)",
                 font=("Consolas", 10),
                 fg=self.renkler["altYazi"],
                 bg=self.renkler["arkaplan"]).pack(pady=(0, 8))

        cF = tk.Frame(pop, bg=self.renkler["arkaplan"])
        cF.pack(fill="both", expand=True, padx=16, pady=4)

        sb = tk.Scrollbar(cF)
        sb.pack(side="right", fill="y")

        metin = tk.Text(cF, font=("Consolas", 10),
                        bg=self.renkler["vurgu"],
                        fg=self.renkler["yazi"],
                        relief="flat", bd=4,
                        yscrollcommand=sb.set)
        metin.pack(fill="both", expand=True)
        sb.config(command=metin.yview)

        for i in range(parSay):
            pPos = 2 ** i
            metin.insert("end", f"{'='*50}\n", "baslik")
            metin.insert("end", f"  P{pPos}  ->  pozisyonu{pPos}(2^{i})\n", "parity")
            metin.insert("end", f"{'='*50}\n", "baslik")
            metin.insert("end", f"  kapsadigi pozisyonlar(AND{pPos}!= 0):\n\n", "bilgi")

            sorumluPozlar = [k for k in range(1, n + 1) if k & pPos]

            satir = "  "
            for k in sorumluPozlar:
                satir += f"[{k}]={self.bellekBitler[k-1]}  "
            metin.insert("end", satir + "\n\n", "bitler")

            xorSatir = "  xor zinciri: "
            sonuc = 0
            for k in sorumluPozlar:
                sonuc ^= self.bellekBitler[k - 1]
                xorSatir += str(self.bellekBitler[k - 1])
                if k != sorumluPozlar[-1]:
                    xorSatir += " ^ "
            xorSatir += f" = {sonuc}"
            metin.insert("end", xorSatir + "\n\n", "xor")

            if sonuc == 0:
                metin.insert("end", f"  OK   P{pPos} = {sonuc}  -> dogru\n\n", "tamam")
            else:
                metin.insert("end", f"  HATA P{pPos} = {sonuc}  -> hatali\n\n", "hata")

        sendrom = sendromHesapla(self.bellekBitler)
        metin.insert("end", f"{'='*50}\n", "baslik")
        metin.insert("end", f"  SENDROM = {sendrom}\n", "parity")
        if sendrom == 0:
            metin.insert("end", "  -> hata yok\n", "tamam")
        else:
            metin.insert("end", f"  -> hatali bit: {sendrom}\n", "hata")
        metin.insert("end", f"{'='*50}\n", "baslik")

        metin.tag_config("baslik", foreground=self.renkler["altYazi"])
        metin.tag_config("parity", foreground=self.renkler["sari"],
                         font=("Consolas", 10, "bold"))
        metin.tag_config("bilgi",  foreground=self.renkler["altYazi"])
        metin.tag_config("bitler", foreground=self.renkler["yazi"])
        metin.tag_config("xor",    foreground=self.renkler["yesil"])
        metin.tag_config("tamam",  foreground=self.renkler["yesil"])
        metin.tag_config("hata",   foreground=self.renkler["hataRengi"])
        metin.configure(state="disabled")


if __name__ == "__main__":
    ana = tk.Tk()
    HammingSimulatoru(ana)
    ana.mainloop()

#hesaplamalar için yeni pencereni kaydı eklenicek








