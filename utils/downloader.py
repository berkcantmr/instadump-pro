# utils/downloader.py
import os
import requests
import time

def download_file(url, username, media_type, prefix="media"):
    """
    Verilen URL'deki dosyayı downloads/username klasörüne indirir.
    """
    if not url: return None

    # Klasör oluştur: downloads/elonmusk/
    folder_path = f"downloads/{username}"
    os.makedirs(folder_path, exist_ok=True)

    # Dosya uzantısını belirle
    extension = "mp4" if media_type == "video" else "jpg"
    
    # Dosya adı: story_17099232.jpg (Çakışmayı önlemek için zaman damgası)
    timestamp = int(time.time() * 1000)
    filename = f"{prefix}_{timestamp}.{extension}"
    file_path = os.path.join(folder_path, filename)

    try:
        # İndirme isteği
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"      ⬇️ İndirildi: {filename}")
            return file_path
        else:
            print(f"      ❌ İndirme başarısız (Status: {response.status_code})")
    except Exception as e:
        print(f"      ❌ İndirme hatası: {e}")
    
    return None