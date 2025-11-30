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
