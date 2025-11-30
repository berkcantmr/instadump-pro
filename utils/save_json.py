# utils/save_json.py
import json
import os

def save_data(new_data, filename="output/output.json"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    final_data = {}
    
    # 1. Eğer dosya varsa, eski veriyi oku
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                if isinstance(existing_data, dict):
                    final_data = existing_data
        except:
            pass # Dosya bozuksa veya boşsa sıfırdan başla

    # 2. Yeni veriyi eski verinin üzerine yaz (Merge/Update)
    # new_data içindeki anahtarlar (profile, posts vb.) eskileri günceller
    final_data.update(new_data)

    # 3. Dosyayı kaydet
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    
    # Konsolu kirletmemek için print'i kaldırdım veya yorum satırı yapabilirsin
    # print(f"💾 Kayıt güncellendi: {filename}")