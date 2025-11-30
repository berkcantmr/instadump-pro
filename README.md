# 🔥 INSTADUMP PRO

**INSTADUMP PRO**, Python ve Playwright kullanılarak geliştirilmiş, gelişmiş bir Instagram arşivleme, analiz ve veri görselleştirme aracıdır.

## 🚀 Özellikler

- **Tam Otomasyon:** Tarayıcı üzerinden insan gibi davranarak veri toplar (Stealth Modu).
- **Güvenli Giriş:** Session yönetimi ile her seferinde şifre girmeye gerek kalmaz.
- **Kapsamlı İndirme:**
  - 📸 Gönderiler (Çoklu kaydırmalı/Carousel postlar dahil)
  - 🟣 Hikayeler (Stories) - *Video ve Fotoğraf ayrımı*
  - 🌟 Öne Çıkanlar (Highlights) - *Kapak, İçerik ve Başlık ayrımı*
  - 👥 Network Analizi (Takipçi/Takip Edilenler ve Karşılıklı Takipler)
- **Görsel Dashboard:** İndirilen verileri `Streamlit` arayüzü ile galeri modunda görüntüleme.
- **Crash Guard:** Tarayıcı kapansa bile kaldığı yerden devam etme veya güvenli çıkış.
- **Akıllı Bypass:** "Video Oynatılamıyor" hatalarını ve ara ekranları otomatik geçer.

## 🛠️ Kurulum

Projeyi bilgisayarınıza kurmak için aşağıdaki adımları sırasıyla uygulayın.

### 1. Repoyu Klonlayın

git clone [https://github.com/berkcantmr/instadump-pro.git](https://github.com/berkcantmr/instadump-pro.git)
cd instadump-pro


2\. Gerekli Paketleri Yükleyin

Tüm kütüphaneleri ve gerekli tarayıcıyı tek seferde kurmak için aşağıdaki bloğu kopyalayıp yapıştırın:



Bash



pip install -r requirements.txt \&\& playwright install chromium

Not: Eğer Windows kullanıyorsanız ve yukarıdaki komut hata verirse, şu iki komutu sırasıyla çalıştırın:



pip install -r requirements.txt



playwright install chromium



💻 Kullanım

1\. Veri Toplama (Scraper)

Aracı başlatmak için terminale şu komutu girin:



Bash



python main.py

Sizi yönlendiren sihirbazı takip edin. İlk açılışta giriş yapmanız ve bir session oluşturmanız istenecektir.



2\. Verileri Görüntüleme (Dashboard)

İndirilen verileri ve analizleri görmek için:



Bash



streamlit run app.py

⚠️ Yasal Uyarı!!!

Bu araç sadece eğitim ve kişisel arşivleme amaçlı geliştirilmiştir. Kullanıcıların Instagram kullanım koşullarına (ToS) uyması kendi sorumluluğundadır. Geliştirici, aracın kötüye kullanımından sorumlu tutulamaz.
