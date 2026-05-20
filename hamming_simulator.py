import tkinter as tk
from tkinter import messagebox

# ─────────────────────────────────────────
#  HAMMING KODU HESAPLAMA FONKSİYONLARI
# ─────────────────────────────────────────

def calculate_parity_bits(m):
    """Kaç tane parity biti gerektiğini hesapla"""
    r = 0
    while (2 ** r) < (m + r + 1):
        r += 1
    return r

def encode_hamming(data_bits):
    """Veriyi Hamming koduna çevir"""
    m = len(data_bits)
    r = calculate_parity_bits(m)
    n = m + r  # toplam bit sayısı

    # Pozisyonları yerleştir (1'den başlar)
    hamming = [0] * (n + 1)  # index 0 kullanılmayacak

    # Veri bitlerini yerleştir (parity pozisyonları hariç)
    j = 0
    for i in range(1, n + 1):
        if i & (i - 1) != 0:  # 2'nin kuvveti değilse → veri biti
            hamming[i] = int(data_bits[j])
            j += 1

    # Parity bitlerini hesapla
    for i in range(r):
        pos = 2 ** i
        parity = 0
        for k in range(1, n + 1):
            if k & pos:
                parity ^= hamming[k]
        hamming[pos] = parity

    return hamming[1:]  # index 1'den başlayarak döndür

def calculate_syndrome(received):
    """Sendromu hesapla → hatalı bit pozisyonu"""
    n = len(received)
    r = 0
    while (2 ** r) < n + 1:
        r += 1

    syndrome = 0
    for i in range(r):
        pos = 2 ** i
        parity = 0
        for k in range(1, n + 1):
            if k & pos:
                parity ^= received[k - 1]
        if parity != 0:
            syndrome += pos

    return syndrome

def correct_error(received, error_pos):
    """Hatalı biti düzelt"""
    corrected = received[:]
    if 0 < error_pos <= len(corrected):
        corrected[error_pos - 1] ^= 1  # biti tersine çevir
    return corrected

def get_parity_positions(n):
    """Parity bit pozisyonlarını döndür"""
    positions = []
    i = 1
    while i <= n:
        positions.append(i)
        i *= 2
    return positions


# ─────────────────────────────────────────
#  ANA UYGULAMA SINIFI
# ─────────────────────────────────────────

class HammingSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Hamming Error-Correcting Code Simülatörü")
        self.root.geometry("950x750")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(True, True)

        # Renk paleti
        self.colors = {
            "bg":         "#1a1a2e",
            "panel":      "#16213e",
            "accent":     "#0f3460",
            "highlight":  "#e94560",
            "green":      "#00b894",
            "yellow":     "#fdcb6e",
            "text":       "#eaeaea",
            "subtext":    "#a0a0b0",
            "parity_bg":  "#2d1b4e",
            "data_bg":    "#1b3a4e",
            "error_bg":   "#4e1b1b",
        }

        self.memory = []          # bellekteki Hamming kodlu veri
        self.original_data = ""   # kullanıcının girdiği orijinal veri
        self.bit_buttons = []     # bit toggle butonları
        self.current_bits = 8

        self._build_ui()

    # ── ARAYÜZ KURULUMU ────────────────────

    def _build_ui(self):
        # Başlık
        title_frame = tk.Frame(self.root, bg=self.colors["bg"])
        title_frame.pack(fill="x", padx=20, pady=(15, 5))

        tk.Label(title_frame,
                 text="⚡ Hamming Error-Correcting Code Simülatörü",
                 font=("Consolas", 18, "bold"),
                 fg=self.colors["highlight"],
                 bg=self.colors["bg"]).pack()

        tk.Label(title_frame,
                 text="BLM230 Bilgisayar Mimarisi",
                 font=("Consolas", 10),
                 fg=self.colors["subtext"],
                 bg=self.colors["bg"]).pack()

        # Ana çerçeve
        main = tk.Frame(self.root, bg=self.colors["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=5)

        # Sol panel (giriş + encode)
        left = tk.Frame(main, bg=self.colors["panel"],
                        relief="ridge", bd=2)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Sağ panel (bellek + hata + düzeltme)
        right = tk.Frame(main, bg=self.colors["panel"],
                         relief="ridge", bd=2)
        right.pack(side="left", fill="both", expand=True)

        self._build_input_panel(left)
        self._build_memory_panel(right)

        # Log alanı
        self._build_log_area()

    def _build_input_panel(self, parent):
        tk.Label(parent, text="📥  VERİ GİRİŞİ & ENCODE",
                 font=("Consolas", 12, "bold"),
                 fg=self.colors["green"],
                 bg=self.colors["panel"]).pack(pady=(12, 4))

        # Bit boyutu seçimi
        bit_frame = tk.Frame(parent, bg=self.colors["panel"])
        bit_frame.pack(pady=4)

        tk.Label(bit_frame, text="Bit Boyutu:",
                 font=("Consolas", 10),
                 fg=self.colors["text"],
                 bg=self.colors["panel"]).pack(side="left", padx=4)

        self.bit_var = tk.IntVar(value=8)
        for val in [8, 16, 32]:
            rb = tk.Radiobutton(bit_frame, text=f"{val} bit",
                                variable=self.bit_var, value=val,
                                font=("Consolas", 10),
                                fg=self.colors["text"],
                                bg=self.colors["panel"],
                                selectcolor=self.colors["accent"],
                                activebackground=self.colors["panel"],
                                command=self._on_bit_change)
            rb.pack(side="left", padx=6)

        # Veri giriş kutusu
        tk.Label(parent,
                 text="İkili Veri Girin (sadece 0 ve 1):",
                 font=("Consolas", 10),
                 fg=self.colors["subtext"],
                 bg=self.colors["panel"]).pack(pady=(8, 2))

        entry_frame = tk.Frame(parent, bg=self.colors["panel"])
        entry_frame.pack(pady=2)

        self.data_entry = tk.Entry(entry_frame,
                                   width=36,
                                   font=("Consolas", 13),
                                   bg=self.colors["accent"],
                                   fg=self.colors["green"],
                                   insertbackground=self.colors["green"],
                                   relief="flat", bd=4)
        self.data_entry.pack(side="left", padx=4)
        self.data_entry.bind("<KeyRelease>", self._validate_input)

        self.len_label = tk.Label(entry_frame,
                                  text="0/8",
                                  font=("Consolas", 10),
                                  fg=self.colors["subtext"],
                                  bg=self.colors["panel"])
        self.len_label.pack(side="left")

        # Encode butonu
        tk.Button(parent,
                  text="🔐  ENCODE & BELLEĞE YAZ",
                  font=("Consolas", 11, "bold"),
                  bg=self.colors["green"],
                  fg="#000000",
                  activebackground="#00a381",
                  relief="flat", bd=0,
                  padx=12, pady=6,
                  cursor="hand2",
                  command=self._encode).pack(pady=10)

        # Hamming kodu gösterimi
        tk.Label(parent, text="Hamming Kodu (Bellekteki Veri):",
                 font=("Consolas", 10),
                 fg=self.colors["subtext"],
                 bg=self.colors["panel"]).pack(pady=(6, 2))

        self.hamming_display = tk.Frame(parent, bg=self.colors["panel"])
        self.hamming_display.pack(pady=4, padx=10)

        # ── Parity adım adım butonu ──
        tk.Button(parent,
                  text="🔎  PARITY HESABINI GÖSTER",
                  font=("Consolas", 10, "bold"),
                  bg=self.colors["accent"],
                  fg=self.colors["yellow"],
                  activebackground="#1a4a7a",
                  relief="flat", bd=0,
                  padx=10, pady=5,
                  cursor="hand2",
                  command=self._show_parity_steps).pack(pady=(4, 2))

        # Legend
        legend = tk.Frame(parent, bg=self.colors["panel"])
        legend.pack(pady=(2, 8))
        for color, label in [(self.colors["parity_bg"], "Parity Biti"),
                              (self.colors["data_bg"],   "Veri Biti")]:
            f = tk.Frame(legend, bg=color, width=14, height=14,
                         relief="flat")
            f.pack(side="left", padx=3)
            tk.Label(legend, text=label,
                     font=("Consolas", 8),
                     fg=self.colors["subtext"],
                     bg=self.colors["panel"]).pack(side="left", padx=(0, 8))

    def _build_memory_panel(self, parent):
        tk.Label(parent, text="💾  BELLEK / HATA / DÜZELTME",
                 font=("Consolas", 12, "bold"),
                 fg=self.colors["yellow"],
                 bg=self.colors["panel"]).pack(pady=(12, 4))

        tk.Label(parent,
                 text="Belleğe yazılmış veri aşağıda.\n"
                      "Herhangi bir bite tıklayarak yapay hata oluşturabilirsiniz.",
                 font=("Consolas", 9),
                 fg=self.colors["subtext"],
                 bg=self.colors["panel"],
                 justify="center").pack(pady=(0, 6))

        # Tıklanabilir bit butonları
        self.bit_frame = tk.Frame(parent, bg=self.colors["panel"])
        self.bit_frame.pack(pady=4, padx=10)

        # Sendrom & düzelt butonları
        btn_row = tk.Frame(parent, bg=self.colors["panel"])
        btn_row.pack(pady=8)

        tk.Button(btn_row,
                  text="🔍  SENDROMU HESAPLA",
                  font=("Consolas", 10, "bold"),
                  bg=self.colors["yellow"],
                  fg="#000000",
                  activebackground="#e0b050",
                  relief="flat", bd=0,
                  padx=8, pady=5,
                  cursor="hand2",
                  command=self._detect_error).pack(side="left", padx=4)

        tk.Button(btn_row,
                  text="✅  HATAYI DÜZELT",
                  font=("Consolas", 10, "bold"),
                  bg=self.colors["highlight"],
                  fg="#ffffff",
                  activebackground="#c73652",
                  relief="flat", bd=0,
                  padx=8, pady=5,
                  cursor="hand2",
                  command=self._correct_error).pack(side="left", padx=4)

        # Sonuç kutusu
        result_frame = tk.Frame(parent, bg=self.colors["accent"],
                                relief="ridge", bd=2)
        result_frame.pack(fill="x", padx=14, pady=6)

        tk.Label(result_frame, text="Sonuç:",
                 font=("Consolas", 10, "bold"),
                 fg=self.colors["subtext"],
                 bg=self.colors["accent"]).pack(anchor="w", padx=8, pady=(6,0))

        self.result_label = tk.Label(result_frame,
                                     text="—",
                                     font=("Consolas", 12, "bold"),
                                     fg=self.colors["text"],
                                     bg=self.colors["accent"],
                                     wraplength=340,
                                     justify="left")
        self.result_label.pack(anchor="w", padx=8, pady=(0, 8))

        # Karşılaştırma tablosu
        tk.Label(parent, text="Veri Karşılaştırması:",
                 font=("Consolas", 10),
                 fg=self.colors["subtext"],
                 bg=self.colors["panel"]).pack(pady=(8, 2))

        self.compare_frame = tk.Frame(parent, bg=self.colors["panel"])
        self.compare_frame.pack(pady=2, padx=10)

    def _build_log_area(self):
        log_outer = tk.Frame(self.root, bg=self.colors["bg"])
        log_outer.pack(fill="x", padx=20, pady=(4, 14))

        tk.Label(log_outer, text="📋  İŞLEM KAYITLARI",
                 font=("Consolas", 10, "bold"),
                 fg=self.colors["subtext"],
                 bg=self.colors["bg"]).pack(anchor="w")

        self.log_text = tk.Text(log_outer,
                                height=5,
                                font=("Consolas", 9),
                                bg=self.colors["accent"],
                                fg=self.colors["green"],
                                relief="flat", bd=4,
                                state="disabled")
        self.log_text.pack(fill="x")

    # ── YARDIMCI FONKSİYONLAR ──────────────

    def _log(self, msg, color=None):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"▶ {msg}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _validate_input(self, event=None):
        val = self.data_entry.get()
        bits = self.bit_var.get()
        clean = ''.join(c for c in val if c in '01')
        if clean != val:
            self.data_entry.delete(0, "end")
            self.data_entry.insert(0, clean)
        self.len_label.config(text=f"{len(clean)}/{bits}")

    def _on_bit_change(self):
        self.data_entry.delete(0, "end")
        self.len_label.config(text=f"0/{self.bit_var.get()}")

    def _clear_hamming_display(self):
        for w in self.hamming_display.winfo_children():
            w.destroy()

    def _clear_bit_buttons(self):
        for w in self.bit_frame.winfo_children():
            w.destroy()
        self.bit_buttons = []

    def _clear_compare(self):
        for w in self.compare_frame.winfo_children():
            w.destroy()

    # ── ENCODE ─────────────────────────────

    def _encode(self):
        data = self.data_entry.get().strip()
        bits = self.bit_var.get()

        if len(data) != bits:
            messagebox.showerror("Hata", f"Lütfen tam olarak {bits} bit girin!\n"
                                         f"Şu an {len(data)} bit girildi.")
            return
        if not all(c in '01' for c in data):
            messagebox.showerror("Hata", "Sadece 0 ve 1 karakterleri girin!")
            return

        self.original_data = data
        self.memory = encode_hamming(data)

        r = calculate_parity_bits(bits)
        n = bits + r
        parity_positions = get_parity_positions(n)

        self._log(f"Giriş verisi ({bits} bit): {data}")
        self._log(f"Parity bit sayısı: {r}  |  Toplam bit: {n}")
        self._log(f"Hamming kodu: {''.join(map(str, self.memory))}")

        # Hamming gösterimi (renkli kutular)
        self._clear_hamming_display()
        for i, bit in enumerate(self.memory):
            pos = i + 1
            is_parity = (pos in parity_positions)
            bg = self.colors["parity_bg"] if is_parity else self.colors["data_bg"]

            cell = tk.Frame(self.hamming_display, bg=bg,
                            relief="solid", bd=1, padx=0, pady=0)
            cell.pack(side="left", padx=1)

            tk.Label(cell, text=str(pos),
                     font=("Consolas", 7),
                     fg=self.colors["subtext"], bg=bg).pack()
            tk.Label(cell, text=str(bit),
                     font=("Consolas", 12, "bold"),
                     fg=self.colors["green"] if is_parity else self.colors["text"],
                     bg=bg,
                     width=2).pack()

        # Tıklanabilir bellek bitleri
        self._build_memory_bits(parity_positions)
        self._clear_compare()
        self.result_label.config(text="Veri encode edildi ve belleğe yazıldı ✓",
                                 fg=self.colors["green"])

    def _build_memory_bits(self, parity_positions):
        self._clear_bit_buttons()
        self.bit_buttons = []

        row0 = tk.Frame(self.bit_frame, bg=self.colors["panel"])
        row0.pack()
        row1 = tk.Frame(self.bit_frame, bg=self.colors["panel"])
        row1.pack()

        for i, bit in enumerate(self.memory):
            pos = i + 1
            is_parity = (pos in parity_positions)
            bg = self.colors["parity_bg"] if is_parity else self.colors["data_bg"]

            cell = tk.Frame(row1, bg=bg, relief="solid", bd=1)
            cell.pack(side="left", padx=1, pady=1)

            pos_lbl = tk.Label(row0, text=str(pos),
                               font=("Consolas", 7),
                               fg=self.colors["subtext"],
                               bg=self.colors["panel"], width=3)
            pos_lbl.pack(side="left", padx=1)

            btn = tk.Button(cell,
                            text=str(bit),
                            font=("Consolas", 11, "bold"),
                            bg=bg,
                            fg=self.colors["text"],
                            relief="flat", bd=0,
                            width=2, height=1,
                            cursor="hand2",
                            command=lambda idx=i: self._toggle_bit(idx))
            btn.pack()
            self.bit_buttons.append(btn)

    # ── BİT TOGGLE (yapay hata) ─────────────

    def _toggle_bit(self, idx):
        if not self.memory:
            return
        self.memory[idx] ^= 1
        btn = self.bit_buttons[idx]
        btn.config(text=str(self.memory[idx]))

        # Orijinal encode ile karşılaştır → hata varsa kırmızı
        original_hamming = encode_hamming(self.original_data)
        if self.memory[idx] != original_hamming[idx]:
            btn.config(bg=self.colors["error_bg"], fg=self.colors["highlight"])
        else:
            # Orijinaline döndü → rengi sıfırla
            pos = idx + 1
            parity_pos = get_parity_positions(len(self.memory))
            bg = self.colors["parity_bg"] if pos in parity_pos else self.colors["data_bg"]
            btn.config(bg=bg, fg=self.colors["text"])

        self._log(f"Bit {idx+1} değiştirildi → yeni değer: {self.memory[idx]}  (yapay hata)")
        self.result_label.config(text="Bit değiştirildi! Sendromu hesaplayın.",
                                 fg=self.colors["yellow"])

    # ── SENDROM HESAPLA ─────────────────────

    def _detect_error(self):
        if not self.memory:
            messagebox.showwarning("Uyarı", "Önce veri encode edin!")
            return

        # Kaç bit bozuldu say
        original_hamming = encode_hamming(self.original_data)
        error_count = sum(1 for a, b in zip(self.memory, original_hamming) if a != b)

        syndrome = calculate_syndrome(self.memory)
        self._log(f"Sendrom değeri: {syndrome}")

        # Çoklu hata uyarısı
        if error_count >= 2:
            self.result_label.config(
                text=f"❌ ÇOKLU HATA TESPİT EDİLDİ! ({error_count} bit bozuk)\n"
                     f"Hamming kodu yalnızca TEK bit hatasını düzeltebilir!\n"
                     f"Sendrom = {syndrome} ama bu değere güvenilmez.",
                fg=self.colors["highlight"])
            self._log(f"UYARI: {error_count} bit aynı anda bozulmuş → düzeltilemez!")
            return

        if syndrome == 0:
            self.result_label.config(
                text="✅ Sendrom = 0  →  Hata YOK! Veri sağlıklı.",
                fg=self.colors["green"])
            self._log("Sonuç: Hata tespit edilmedi.")
        else:
            self.result_label.config(
                text=f"⚠️  Sendrom = {syndrome}  →  Bit {syndrome} hatalı!\n"
                     f"(Pozisyon {syndrome} düzeltilmeyi bekliyor)",
                fg=self.colors["highlight"])
            self._log(f"Sonuç: Pozisyon {syndrome} hatalı tespit edildi!")
            if 0 < syndrome <= len(self.bit_buttons):
                self.bit_buttons[syndrome - 1].config(
                    bg=self.colors["error_bg"])

    # ── HATAYI DÜZELT ───────────────────────

    def _correct_error(self):
        if not self.memory:
            messagebox.showwarning("Uyarı", "Önce veri encode edin!")
            return

        # Çoklu hata varsa düzeltme yapma
        original_hamming = encode_hamming(self.original_data)
        error_count = sum(1 for a, b in zip(self.memory, original_hamming) if a != b)
        if error_count >= 2:
            messagebox.showerror("Düzeltilemez",
                                 f"{error_count} bit aynı anda bozuk!\n"
                                 "Hamming kodu sadece tek bit hatasını düzeltebilir.")
            return

        syndrome = calculate_syndrome(self.memory)
        if syndrome == 0:
            self.result_label.config(
                text="✅ Düzeltilecek hata yok, veri temiz!",
                fg=self.colors["green"])
            return

        self.memory = correct_error(self.memory, syndrome)

        # Butonu güncelle
        btn = self.bit_buttons[syndrome - 1]
        btn.config(text=str(self.memory[syndrome - 1]))
        pos = syndrome
        parity_pos = get_parity_positions(len(self.memory))
        bg = self.colors["parity_bg"] if pos in parity_pos else self.colors["data_bg"]
        btn.config(bg=bg, fg=self.colors["text"])

        self._log(f"Pozisyon {syndrome} düzeltildi → bit {self.memory[syndrome-1]} yapıldı")

        # Düzeltilmiş veriyi çıkar
        n = len(self.memory)
        parity_positions = get_parity_positions(n)
        recovered = [str(self.memory[i])
                     for i in range(n)
                     if (i + 1) not in parity_positions]
        recovered_str = ''.join(recovered)

        self.result_label.config(
            text=f"✅ Hata düzeltildi!\n"
                 f"Orijinal veri : {self.original_data}\n"
                 f"Kurtarılan    : {recovered_str}\n"
                 f"Eşleşiyor mu? : {'✔ EVET' if recovered_str == self.original_data else '✘ HAYIR'}",
            fg=self.colors["green"])

        self._show_comparison(self.original_data, recovered_str)

    # ── KARŞILAŞTIRMA TABLOSU ───────────────

    def _show_comparison(self, original, recovered):
        self._clear_compare()

        headers = ["", "Veri"]
        rows = [("Orijinal", original), ("Kurtarılan", recovered)]

        for col, h in enumerate(headers):
            tk.Label(self.compare_frame, text=h,
                     font=("Consolas", 9, "bold"),
                     fg=self.colors["yellow"],
                     bg=self.colors["panel"]).grid(
                         row=0, column=col, padx=4, pady=2)

        for row_i, (label, data) in enumerate(rows, start=1):
            tk.Label(self.compare_frame, text=label,
                     font=("Consolas", 9),
                     fg=self.colors["subtext"],
                     bg=self.colors["panel"]).grid(
                         row=row_i, column=0, padx=4, pady=1)

            bit_frame = tk.Frame(self.compare_frame, bg=self.colors["panel"])
            bit_frame.grid(row=row_i, column=1, padx=4, pady=1)

            for i, bit in enumerate(data):
                match = (len(original) > i and original[i] == bit)
                fg = self.colors["green"] if match else self.colors["highlight"]
                tk.Label(bit_frame, text=bit,
                         font=("Consolas", 10, "bold"),
                         fg=fg,
                         bg=self.colors["panel"]).pack(side="left", padx=1)


    # ── PARITY ADIM ADIM PENCERESİ ──────────

    def _show_parity_steps(self):
        if not self.memory:
            messagebox.showwarning("Uyarı", "Önce veri encode edin!")
            return

        n = len(self.memory)
        r = calculate_parity_bits(len(self.original_data))

        win = tk.Toplevel(self.root)
        win.title("Parity Bit Hesaplama Adımları")
        win.geometry("620x500")
        win.configure(bg=self.colors["bg"])

        tk.Label(win,
                 text="🔎 Parity Bit Hesaplama Adımları",
                 font=("Consolas", 13, "bold"),
                 fg=self.colors["yellow"],
                 bg=self.colors["bg"]).pack(pady=(14, 4))

        tk.Label(win,
                 text=f"Hamming kodu: {''.join(map(str, self.memory))}   "
                      f"(toplam {n} bit, {r} parity biti)",
                 font=("Consolas", 10),
                 fg=self.colors["subtext"],
                 bg=self.colors["bg"]).pack(pady=(0, 8))

        frame = tk.Frame(win, bg=self.colors["bg"])
        frame.pack(fill="both", expand=True, padx=16, pady=4)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text = tk.Text(frame,
                       font=("Consolas", 10),
                       bg=self.colors["accent"],
                       fg=self.colors["text"],
                       relief="flat", bd=4,
                       yscrollcommand=scrollbar.set)
        text.pack(fill="both", expand=True)
        scrollbar.config(command=text.yview)

        for i in range(r):
            pos = 2 ** i
            text.insert("end", f"{'='*50}\n", "header")
            text.insert("end", f"  P{pos}  →  Pozisyon {pos} (2^{i}) Parity Biti\n", "parity")
            text.insert("end", f"{'='*50}\n", "header")
            text.insert("end", f"  Hangi bitlere bakıyor? (pozisyon & {pos} != 0 olanlar)\n\n", "info")

            covered = [k for k in range(1, n + 1) if k & pos]

            line = "  Pozisyonlar: "
            for k in covered:
                line += f"[{k}]={self.memory[k-1]}  "
            text.insert("end", line + "\n\n", "bits")

            xor_line = "  XOR zinciri: "
            result = 0
            for k in covered:
                result ^= self.memory[k - 1]
                xor_line += str(self.memory[k-1])
                if k != covered[-1]:
                    xor_line += " xor "
            xor_line += f" = {result}"
            text.insert("end", xor_line + "\n\n", "xor")

            if result == 0:
                text.insert("end", f"  OK  P{pos} = {result}  Bu parity biti DOGRU\n\n", "ok")
            else:
                text.insert("end", f"  !!  P{pos} = {result}  Bu parity biti HATALI\n\n", "err")

        syndrome = calculate_syndrome(self.memory)
        text.insert("end", f"{'='*50}\n", "header")
        text.insert("end", f"  SENDROM SONUCU = {syndrome}\n", "parity")
        if syndrome == 0:
            text.insert("end", "  Hata yok!\n", "ok")
        else:
            text.insert("end", f"  Hatali bit pozisyonu: {syndrome}\n", "err")
        text.insert("end", f"{'='*50}\n", "header")

        text.tag_config("header", foreground=self.colors["subtext"])
        text.tag_config("parity", foreground=self.colors["yellow"],
                        font=("Consolas", 10, "bold"))
        text.tag_config("info",   foreground=self.colors["subtext"])
        text.tag_config("bits",   foreground=self.colors["text"])
        text.tag_config("xor",    foreground=self.colors["green"])
        text.tag_config("ok",     foreground=self.colors["green"])
        text.tag_config("err",    foreground=self.colors["highlight"])
        text.configure(state="disabled")


# ─────────────────────────────────────────
#  ÇALIŞTIR
# ─────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = HammingSimulator(root)
    root.mainloop()