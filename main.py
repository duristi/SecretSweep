import os
import re
import json
import threading
import subprocess
import sys
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

# =============================================================================
# 1. AYARLAR VE REGEX TANIMLARI
# =============================================================================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

PATTERNS = {
    "VISA": r"\b4[0-9]{12}(?:[0-9]{3})?\b",
    "MASTER": r"\b5[1-5][0-9]{14}\b",
    "AMEX": r"\b3[47][0-9]{13}\b",
    "TR_IBAN": r"\bTR\d{2}\s?(\d{4}\s?){5}\d{2}\b",
    "TCKN": r"\b[1-9][0-9]{9}[02468]\b",
    "AWS_KEY": r"\bAKIA[0-9A-Z]{16}\b",
    "PRIVATE_KEY": r"-----BEGIN [A-Z]+ PRIVATE KEY-----",
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    # Yeni örüntüler
    "JWT_TOKEN": r"\beyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\b",
    "GITHUB_TOKEN": r"\b(?:ghp|gho|ghs)_[A-Za-z0-9]{36}\b",
    "STRIPE_KEY": r"\b(?:sk|pk)_(?:live|test)_[A-Za-z0-9]{24,}\b",
    "GOOGLE_API_KEY": r"\bAIza[A-Za-z0-9\-_]{35}\b",
    "BEARER_TOKEN": r"(?i)bearer\s+([A-Za-z0-9\-_\.]{20,})",
}

IGNORE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.exe', '.dll', '.zip', '.pdf', '.docx', '.git'}
CREDIT_CARDS = ["VISA", "MASTER", "AMEX"]

# =============================================================================
# 2. DİNAMİK LOGO OLUŞTURUCU (Konsept 3)
# =============================================================================
def create_app_logo(size=(100, 100)):
    """
    Bu fonksiyon, harici bir dosya kullanmadan RAM üzerinde
    Minimalist bir 'Kod Dosyası ve Büyüteç' ikonu çizer.
    """
    # Şeffaf arka planlı bir resim oluştur
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    w, h = size
    
    # Renkler
    icon_color = "#E0E0E0"  # Açık Gri (Dosya için)
    accent_color = "#3B8ED0" # CustomTkinter Mavisi (Büyüteç için)
    
    # 1. Dosya Kağıdı Çizimi (Dikdörtgen)
    margin = w // 5
    draw.rounded_rectangle(
        (margin, margin, w - margin, h - 5),
        radius=8,
        outline=icon_color,
        width=3
    )
    
    # 2. Kod Simgesi (< >)
    # Basit çizgilerle < > işareti yapalım
    center_x, center_y = w // 2, h // 2
    
    # Sol ok (<)
    draw.line((center_x - 10, center_y - 10, center_x - 20, center_y, center_x - 10, center_y + 10), fill=icon_color, width=3)
    # Sağ ok (>)
    draw.line((center_x + 10, center_y - 10, center_x + 20, center_y, center_x + 10, center_y + 10), fill=icon_color, width=3)
    # Slash (/)
    draw.line((center_x + 5, center_y - 15, center_x - 5, center_y + 15), fill=icon_color, width=2)

    # 3. Büyüteç Çizimi (Sağ alt köşeye)
    glass_radius = w // 5
    glass_center_x = w - margin - 5
    glass_center_y = h - margin - 5
    
    # Sapı
    draw.line((glass_center_x, glass_center_y, glass_center_x + 15, glass_center_y + 15), fill=accent_color, width=5)
    # Çerçevesi
    draw.ellipse(
        (glass_center_x - glass_radius, glass_center_y - glass_radius, 
         glass_center_x + glass_radius, glass_center_y + glass_radius),
        outline=accent_color,
        width=4
    )
    
    return img

# =============================================================================
# 3. ANA UYGULAMA
# =============================================================================

class SecretSweepApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Pencere Ayarları ---
        self.title("SecretSweep - Code Cleaner")
        self.geometry("900x650")
        
        # Grid Yapısı
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Logoyu Oluştur (Header ve Hakkında sayfası için)
        self.logo_img_large = ctk.CTkImage(light_image=create_app_logo((150, 150)), 
                                           dark_image=create_app_logo((150, 150)), size=(120, 120))
                                           
        self.logo_img_small = ctk.CTkImage(light_image=create_app_logo((64, 64)), 
                                           dark_image=create_app_logo((64, 64)), size=(40, 40))

        # --- SEKMELİ YAPI ---
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.tab_scan = self.tabview.add("🔍 Tarama Merkezi")
        self.tab_faq = self.tabview.add("❓ S.S.S")
        self.tab_about = self.tabview.add("ℹ️ Hakkında")

        self.setup_scan_tab()
        self.setup_faq_tab()
        self.setup_about_tab()

        self.target_folder = ""
        self.is_scanning = False
        self._cancel_scan = False
        self._last_report_path = ""

    # -------------------------------------------------------------------------
    # TAB 1: TARAMA ARAYÜZÜ
    # -------------------------------------------------------------------------
    def setup_scan_tab(self):
        self.tab_scan.grid_columnconfigure(0, weight=1)
        self.tab_scan.grid_rowconfigure(2, weight=1)

        # Header (Logo + İsim)
        header_frame = ctk.CTkFrame(self.tab_scan, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=(10, 20), sticky="ew")
        
        # Dinamik oluşturulan küçük logoyu kullan
        lbl_logo = ctk.CTkLabel(header_frame, text="", image=self.logo_img_small)
        lbl_logo.pack(side="left", padx=10)

        lbl_title = ctk.CTkLabel(header_frame, text="SecretSweep", font=("Roboto", 26, "bold"))
        lbl_title.pack(side="left")
        
        lbl_subtitle = ctk.CTkLabel(header_frame, text="|  Source Code Security Scanner", font=("Roboto", 14), text_color="gray")
        lbl_subtitle.pack(side="left", padx=10, pady=(5,0))

        # Kontrol Paneli
        control_frame = ctk.CTkFrame(self.tab_scan)
        control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.btn_select = ctk.CTkButton(control_frame, text="📁 Proje Klasörü Seç", command=self.select_folder, font=("Roboto", 14))
        self.btn_select.grid(row=0, column=0, padx=20, pady=20)

        self.lbl_path = ctk.CTkLabel(control_frame, text="Hedef klasör bekleniyor...", text_color="gray", font=("Consolas", 12))
        self.lbl_path.grid(row=0, column=1, padx=10, sticky="w")

        self.btn_start = ctk.CTkButton(control_frame, text="TARAMAYI BAŞLAT ▶", command=self.start_scan_thread, state="disabled", fg_color="#2CC985", text_color="white", font=("Roboto", 14, "bold"))
        self.btn_start.grid(row=0, column=2, padx=20, pady=20)

        self.btn_cancel = ctk.CTkButton(control_frame, text="⏹ İptal", command=self.cancel_scan, state="disabled", fg_color="#E05252", text_color="white", font=("Roboto", 14, "bold"))
        self.btn_cancel.grid(row=0, column=3, padx=(0, 20), pady=20)

        self.btn_open_report = ctk.CTkButton(control_frame, text="📄 Raporu Aç", command=self.open_report, state="disabled", font=("Roboto", 13))
        self.btn_open_report.grid(row=0, column=4, padx=(0, 20), pady=20)

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(control_frame, height=15)
        self.progress_bar.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="ew")
        self.progress_bar.set(0)

        # Terminal / Log Ekranı
        self.textbox = ctk.CTkTextbox(self.tab_scan, font=("Consolas", 13), activate_scrollbars=True)
        self.textbox.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.textbox.insert("0.0", ">>> SecretSweep System Ready...\n>>> Waiting for target directory...\n")

        # Footer Status
        self.lbl_status = ctk.CTkLabel(self.tab_scan, text="Sistem Boşta", anchor="w", font=("Roboto", 11))
        self.lbl_status.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

    # -------------------------------------------------------------------------
    # TAB 2: S.S.S
    # -------------------------------------------------------------------------
    def setup_faq_tab(self):
        faq_content = """
        SECRET SWEEP - KULLANIM KILAVUZU

        [1] BU ARAÇ NEDİR?
        SecretSweep, yazılım projelerinin kaynak kodlarında unutulmuş hassas verileri
        (Kredi Kartı, API Key, Özel Anahtar vb.) tespit eden bir güvenlik aracıdır.

        [2] NASIL KULLANILIR?
        1. 'Tarama Merkezi' sekmesine gidin.
        2. 'Proje Klasörü Seç' butonu ile taramak istediğiniz dizini seçin.
        3. 'TARAMAYI BAŞLAT' butonuna basın.
        4. Sonuçlar ekranda belirecek ve otomatik olarak JSON raporu oluşturulacaktır.
        5. Tarama bittikten sonra 'Raporu Aç' butonu ile raporu açabilirsiniz.
        6. Uzun süren taramaları 'İptal' butonu ile durdurabilirsiniz.

        [3] TESPİT EDİLEN VERİ TİPLERİ
        - Kredi Kartı: VISA, MASTER, AMEX (Luhn algoritması ile doğrulanır)
        - TR_IBAN: Türkiye IBAN numarası
        - TCKN: TC Kimlik Numarası (algoritma ile doğrulanır)
        - AWS_KEY: AWS erişim anahtarı (AKIA...)
        - PRIVATE_KEY: PEM özel anahtar başlığı
        - EMAIL: E-posta adresi
        - JWT_TOKEN: JSON Web Token (eyJ...)
        - GITHUB_TOKEN: GitHub kişisel/OAuth/Server token
        - STRIPE_KEY: Stripe API anahtarı
        - GOOGLE_API_KEY: Google API anahtarı (AIza...)
        - BEARER_TOKEN: HTTP Authorization Bearer token

        [4] GÜVENLİK NOTU
        - Bu uygulama tamamen çevrimdışı (offline) çalışır.
        - Bulunan veriler dışarıya gönderilmez.
        - Bu yazılım sadece eğitim ve güvenlik testi amaçlı geliştirilmiştir. Kendi projelerinizin güvenliğini sağlamak için kullanınız. Başka sistemlerde izinsiz kullanımdan doğacak sorumluluk kullanıcıya aittir.
        """
        textbox_faq = ctk.CTkTextbox(self.tab_faq, font=("Consolas", 14))
        textbox_faq.pack(expand=True, fill="both", padx=20, pady=20)
        textbox_faq.insert("0.0", faq_content)
        textbox_faq.configure(state="disabled")

    # -------------------------------------------------------------------------
    # TAB 3: HAKKINDA
    # -------------------------------------------------------------------------
    def setup_about_tab(self):
        frame_about = ctk.CTkFrame(self.tab_about, fg_color="transparent")
        frame_about.pack(expand=True)

        # Büyük Logoyu Kullan
        ctk.CTkLabel(frame_about, text="", image=self.logo_img_large).pack(pady=20)

        ctk.CTkLabel(frame_about, text="SecretSweep", font=("Roboto", 32, "bold")).pack()
        ctk.CTkLabel(frame_about, text="v2.2 Stable", font=("Roboto", 16), text_color="#2CC985").pack(pady=(0, 20))

        info_text = "Geliştirici: Gökmen Durişti\nVizyon: 2025 Security Tools"
        ctk.CTkLabel(frame_about, text=info_text, font=("Roboto", 18), text_color="#aebed4").pack(pady=10)

        ctk.CTkLabel(frame_about, text="Python & CustomTkinter ile geliştirilmiştir.", font=("Roboto", 12), text_color="gray").pack(pady=30)

    # -------------------------------------------------------------------------
    # MANTIK VE İŞLEVLER
    # -------------------------------------------------------------------------
    def open_report(self):
        if self._last_report_path and os.path.isfile(self._last_report_path):
            try:
                if sys.platform.startswith("win"):
                    os.startfile(self._last_report_path)
                elif sys.platform == "darwin":
                    subprocess.run(["open", self._last_report_path], check=True)
                else:
                    subprocess.run(["xdg-open", self._last_report_path], check=True)
            except Exception:
                messagebox.showerror("Hata", f"Rapor açılamadı:\n{self._last_report_path}")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.target_folder = folder
            # Yolu kısalt (örn: .../Users/Desktop/Project)
            display_path = "..." + folder[-45:] if len(folder) > 45 else folder
            self.lbl_path.configure(text=f"Hedef: {display_path}", text_color="#2CC985")
            self.btn_start.configure(state="normal")
            self.log_message(f">>> Target Locked: {folder}")

    def log_message(self, message):
        self.textbox.insert("end", f"{message}\n")
        self.textbox.see("end")

    def validate_luhn(self, card_number):
        digits = [int(d) for d in str(card_number) if d.isdigit()]
        if not digits:
            return False
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                doubled = digit * 2
                checksum += doubled if doubled < 10 else doubled - 9
            else:
                checksum += digit
        return checksum % 10 == 0

    def validate_tckn(self, tckn_str):
        """TC Kimlik Numarası algoritması ile doğrulama yapar."""
        digits_only = "".join(c for c in tckn_str if c.isdigit())
        if len(digits_only) != 11 or digits_only[0] == "0":
            return False
        d = [int(c) for c in digits_only]
        # 10. hane: tek konumdaki rakamlar toplamının 7 katı - çift konumdaki toplamı, mod 10
        if (sum(d[i] for i in range(0, 9, 2)) * 7 - sum(d[i] for i in range(1, 8, 2))) % 10 != d[9]:
            return False
        # 11. hane: ilk 10 rakamın toplamının mod 10'u
        if sum(d[0:10]) % 10 != d[10]:
            return False
        return True

    def start_scan_thread(self):
        if not self.target_folder: return
        self.is_scanning = True
        self._cancel_scan = False
        self.btn_start.configure(state="disabled")
        self.btn_select.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.progress_bar.set(0)
        self.textbox.delete("1.0", "end")
        threading.Thread(target=self.run_scan, daemon=True).start()

    def cancel_scan(self):
        self._cancel_scan = True
        self.btn_cancel.configure(state="disabled")
        self.after(0, lambda: self.lbl_status.configure(text="İptal ediliyor..."))

    def run_scan(self):
        start_time = datetime.now()
        self.after(0, lambda: self.log_message(f">>> SCAN STARTED AT {start_time.strftime('%H:%M:%S')}"))
        self.after(0, lambda: self.log_message("-" * 60))
        
        file_list = []
        for root, _, files in os.walk(self.target_folder):
            if any(x in root for x in [".git", "node_modules", "venv", "__pycache__"]): continue
            for file in files:
                if os.path.splitext(file)[1].lower() not in IGNORE_EXTENSIONS:
                    file_list.append(os.path.join(root, file))
        
        total_files = len(file_list)
        found_issues = []
        error_count = 0

        if total_files == 0:
            self.after(0, lambda: self.log_message(">>> No eligible files found in the selected directory."))
            self.after(0, lambda: self.lbl_status.configure(text="Taranacak dosya bulunamadı."))
            self.after(0, self._reset_buttons)
            return

        for index, file_path in enumerate(file_list):
            if self._cancel_scan:
                self.after(0, lambda: self.log_message(">>> SCAN CANCELLED BY USER."))
                break

            progress = (index + 1) / total_files
            basename = os.path.basename(file_path)
            self.after(0, lambda p=progress, n=basename: (
                self.progress_bar.set(p),
                self.lbl_status.configure(text=f"Scanning: {n}")
            ))

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_no, line in enumerate(f, 1):
                        if len(line) > 2000: continue
                        
                        for label, pattern in PATTERNS.items():
                            matches = re.finditer(pattern, line)
                            for match in matches:
                                content = match.group()
                                clean = content.replace(" ", "").replace("-", "")
                                
                                if label in CREDIT_CARDS and not self.validate_luhn(clean):
                                    continue

                                if label == "TCKN" and not self.validate_tckn(clean):
                                    continue

                                masked = clean[:2] + "****" + clean[-2:]
                                issue = {"file": file_path, "line": line_no, "type": label, "data": masked}
                                found_issues.append(issue)
                                msg = f"🚨 [MATCH: {label}] -> {os.path.basename(file_path)} : Ln {line_no}"
                                self.after(0, lambda m=msg: self.log_message(m))
            except Exception as e:
                error_count += 1
                err_msg = f"⚠️ [HATA] Dosya okunamadı: {os.path.basename(file_path)}"
                self.after(0, lambda m=err_msg: self.log_message(m))

        elapsed = (datetime.now() - start_time).total_seconds()
        elapsed_str = f"{elapsed:.1f}s"

        if not self._cancel_scan:
            # Raporlama
            report_name = f"SecretSweep_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            report_path = os.path.join(self.target_folder, report_name)
            try:
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(found_issues, f, ensure_ascii=False, indent=4)
                report_saved = True
            except Exception as e:
                report_saved = False
                report_path = str(e)

            def _finish():
                self.lbl_status.configure(text=f"Tarama Tamamlandı. ({elapsed_str})")
                self.log_message("-" * 60)
                self.log_message(f">>> SCAN COMPLETE. {len(found_issues)} ISSUES FOUND. ({elapsed_str}, {error_count} dosya okunamadı)")
                if report_saved:
                    self.log_message(f">>> Report saved to: {report_path}")
                    self._last_report_path = report_path
                    self.btn_open_report.configure(state="normal")
                    messagebox.showinfo(
                        "Tarama Bitti",
                        f"İşlem Tamamlandı!\n"
                        f"Bulunan riskli veri: {len(found_issues)}\n"
                        f"Geçen süre: {elapsed_str}\n"
                        f"Okunamayan dosya: {error_count}\n"
                        f"Rapor: {report_path}"
                    )
                else:
                    messagebox.showwarning(
                        "Tarama Bitti",
                        f"Tarama tamamlandı fakat rapor kaydedilemedi.\n"
                        f"Bulunan riskli veri: {len(found_issues)}\n"
                        f"Geçen süre: {elapsed_str}"
                    )
            self.after(0, _finish)
        else:
            self.after(0, lambda: self.lbl_status.configure(text="Tarama iptal edildi."))

        self.after(0, self._reset_buttons)

    def _reset_buttons(self):
        self.is_scanning = False
        self.btn_start.configure(state="normal")
        self.btn_select.configure(state="normal")
        self.btn_cancel.configure(state="disabled")

if __name__ == "__main__":
    app = SecretSweepApp()
    app.mainloop()