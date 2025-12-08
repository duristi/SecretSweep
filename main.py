import os
import re
import json
import threading
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
    "TCKN": r"\b[1-9]{1}[0-9]{9}[0,2,4,6,8]{1}\b",
    "AWS_KEY": r"\bAKIA[0-9A-Z]{16}\b",
    "PRIVATE_KEY": r"-----BEGIN [A-Z]+ PRIVATE KEY-----",
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
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

        [3] GÜVENLİK NOTU
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
        ctk.CTkLabel(frame_about, text="v2.1 Stable", font=("Roboto", 16), text_color="#2CC985").pack(pady=(0, 20))

        info_text = "Geliştirici: Gökmen Durişti\nVizyon: 2025 Security Tools"
        ctk.CTkLabel(frame_about, text=info_text, font=("Roboto", 18), text_color="#aebed4").pack(pady=10)

        ctk.CTkLabel(frame_about, text="Python & CustomTkinter ile geliştirilmiştir.", font=("Roboto", 12), text_color="gray").pack(pady=30)

    # -------------------------------------------------------------------------
    # MANTIK VE İŞLEVLER
    # -------------------------------------------------------------------------
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
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                doubled = digit * 2
                checksum += doubled if doubled < 10 else doubled - 9
            else:
                checksum += digit
        return checksum % 10 == 0

    def start_scan_thread(self):
        if not self.target_folder: return
        self.is_scanning = True
        self.btn_start.configure(state="disabled")
        self.btn_select.configure(state="disabled")
        self.progress_bar.set(0)
        self.textbox.delete("1.0", "end")
        threading.Thread(target=self.run_scan, daemon=True).start()

    def run_scan(self):
        self.log_message(f">>> SCAN STARTED AT {datetime.now().strftime('%H:%M:%S')}")
        self.log_message("-" * 60)
        
        file_list = []
        for root, _, files in os.walk(self.target_folder):
            if any(x in root for x in [".git", "node_modules", "venv", "__pycache__"]): continue
            for file in files:
                if os.path.splitext(file)[1].lower() not in IGNORE_EXTENSIONS:
                    file_list.append(os.path.join(root, file))
        
        total_files = len(file_list)
        found_issues = []
        
        for index, file_path in enumerate(file_list):
            try:
                progress = (index + 1) / total_files
                self.progress_bar.set(progress)
                self.lbl_status.configure(text=f"Scanning: {os.path.basename(file_path)}")
                
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

                                masked = clean[:2] + "****" + clean[-2:]
                                issue = {"file": file_path, "line": line_no, "type": label, "data": masked}
                                found_issues.append(issue)
                                self.log_message(f"🚨 [MATCH: {label}] -> {os.path.basename(file_path)} : Ln {line_no}")
            except Exception:
                pass

        # Raporlama
        report_name = f"SecretSweep_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(report_name, 'w', encoding='utf-8') as f:
            json.dump(found_issues, f, ensure_ascii=False, indent=4)
        
        self.is_scanning = False
        self.btn_start.configure(state="normal")
        self.btn_select.configure(state="normal")
        self.lbl_status.configure(text="Tarama Tamamlandı.")
        self.log_message("-" * 60)
        self.log_message(f">>> SCAN COMPLETE. {len(found_issues)} ISSUES FOUND.")
        self.log_message(f">>> Report saved to: {report_name}")
        messagebox.showinfo("Tarama Bitti", f"İşlem Tamamlandı!\nToplam {len(found_issues)} adet riskli veri bulundu.")

if __name__ == "__main__":
    app = SecretSweepApp()
    app.mainloop()