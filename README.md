# 🐍 SecretSweep v2.2

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)

**SecretSweep**, geliştiriciler için tasarlanmış, proje dosyaları içinde unutulmuş hassas verileri (Kredi Kartı, API Anahtarları, TCKN vb.) tespit eden, modern arayüze sahip bir **Açık Kaynak Kodlu veri keşif** aracıdır.

---

## 🚀 Özellikler

* **🕵️‍♂️ Kod Odaklı Tarama:** Kaynak kodları (.py, .js, .txt vb.) tarar; resim ve binary dosyaları atlar.
* **🛡️ Akıllı Doğrulama:** Luhn Algoritması ile "sahte" kredi kartı numaralarını eler; TCKN algoritması ile geçersiz kimlik numaralarını filtreler.
* **🎨 Modern Arayüz:** CustomTkinter ile geliştirilmiş, Dark Mode destekli şık tasarım.
* **📊 Dinamik Logo:** Harici resim dosyasına ihtiyaç duymaz, logoyu kod çalışırken RAM üzerinde çizer.
* **📂 Raporlama:** Sonuçları otomatik olarak detaylı bir JSON dosyası olarak kaydeder; raporu tek tıkla açma butonu içerir.
* **⏹ Tarama İptali:** Uzun süren taramaları dilediğiniz an durdurabilirsiniz.
* **⏱️ Geçen Süre:** Tarama bitince kaç saniye sürdüğü gösterilir.
* **⚠️ Hata Raporlama:** Okunamayan dosyalar sessizce geçilmez; log ekranında bildirilir.

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
5. Tarama bittikten sonra **📄 Raporu Aç** butonu ile raporu doğrudan açabilirsiniz.

## 🔍 Tespit Edilen Veri Tipleri

| Tür | Açıklama |
|-----|----------|
| VISA | Visa kredi kartı numarası (Luhn doğrulamalı) |
| MASTER | Mastercard numarası (Luhn doğrulamalı) |
| AMEX | American Express numarası (Luhn doğrulamalı) |
| TR_IBAN | Türkiye IBAN numarası |
| TCKN | TC Kimlik Numarası (algoritma doğrulamalı) |
| AWS_KEY | AWS Erişim Anahtarı (AKIA...) |
| PRIVATE_KEY | PEM formatında özel anahtar başlığı |
| EMAIL | E-posta adresi |
| JWT_TOKEN | JSON Web Token (eyJ...) |
| GITHUB_TOKEN | GitHub Personal/OAuth/Server token (ghp\_, gho\_, ghs\_) |
| STRIPE_KEY | Stripe API anahtarı (sk\_/pk\_live/test\_...) |
| GOOGLE_API_KEY | Google API anahtarı (AIza...) |
| BEARER_TOKEN | HTTP Authorization Bearer token |

## ⚠️ Güvenlik Notu

Bu uygulama tamamen çevrimdışı (offline) çalışır. Bulunan veriler dışarıya gönderilmez. Bu yazılım yalnızca eğitim ve güvenlik testi amacıyla geliştirilmiştir; yalnızca kendi projelerinizin güvenliğini denetlemek için kullanınız.

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında dağıtılmaktadır.

