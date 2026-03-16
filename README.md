# 🐍 SecretSweep v2.1

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)

**SecretSweep**, geliştiriciler için tasarlanmış, proje dosyaları içinde unutulmuş hassas verileri (Kredi Kartı, API Anahtarları, TCKN vb.) tespit eden, modern arayüze sahip bir **Açık Kaynak Kodlu veri keşif** aracıdır.

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
   git clone https://github.com/duristi/SecretSweep.git
   cd SecretSweep
   ```

2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Kullanım

```bash
python main.py
```

1. **Tarama Merkezi** sekmesine gidin.
2. **📁 Proje Klasörü Seç** butonuna tıklayarak taramak istediğiniz dizini seçin.
3. **TARAMAYI BAŞLAT** butonuna basın.
4. Sonuçlar ekranda görüntülenecek ve otomatik olarak bir JSON raporu, seçilen klasörün içine kaydedilecektir.

## 🔍 Tespit Edilen Veri Tipleri

| Tür | Açıklama |
|-----|----------|
| VISA | Visa kredi kartı numarası (Luhn doğrulamalı) |
| MASTER | Mastercard numarası (Luhn doğrulamalı) |
| AMEX | American Express numarası (Luhn doğrulamalı) |
| TR_IBAN | Türkiye IBAN numarası |
| TCKN | Türkiye Cumhuriyeti Kimlik Numarası |
| AWS_KEY | AWS Erişim Anahtarı (AKIA...) |
| PRIVATE_KEY | PEM formatında özel anahtar başlığı |
| EMAIL | E-posta adresi |

## ⚠️ Güvenlik Notu

Bu uygulama tamamen çevrimdışı (offline) çalışır. Bulunan veriler dışarıya gönderilmez. Bu yazılım yalnızca eğitim ve güvenlik testi amacıyla geliştirilmiştir; yalnızca kendi projelerinizin güvenliğini denetlemek için kullanınız.

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında dağıtılmaktadır.

