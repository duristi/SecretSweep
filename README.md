# 🐍 SecretSweep v2.1

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)

**SecretSweep**, geliştiriciler için tasarlanmış, proje dosyaları içinde unutulmuş hassas verileri (Kredi Kartı, API Anahtarları, TCKN vb.) tespit eden, modern arayüze sahip bir **Açık Kaynak Kodlu DLP (Data Loss Prevention)** aracıdır.

---

## 🚀 Özellikler

* **🕵️‍♂️ Kod Odaklı Tarama:** Kaynak kodları (.py, .js, .txt vb.) tarar; resim ve binary dosyaları atlar.
* **🛡️ Akıllı Doğrulama:** Luhn Algoritması ile "sahte" kredi kartı numaralarını eler, sadece matematiksel olarak geçerli olanları raporlar.
* **🎨 Modern Arayüz:** CustomTkinter ile geliştirilmiş, Dark Mode destekli şık tasarım.
* **📊 Dinamik Logo:** Harici resim dosyasına ihtiyaç duymaz, logoyu kod çalışırken RAM üzerinde çizer.
* **📂 Raporlama:** Sonuçları otomatik olarak detaylı bir JSON dosyası olarak kaydeder.

## 🛠️ Kurulum

1. Projeyi bilgisayarınıza indirin:
   ```bash
   git clone [https://github.com/KULLANICI_ADINIZ/SecretSweep.git](https://github.com/KULLANICI_ADINIZ/SecretSweep.git)
   cd SecretSweep