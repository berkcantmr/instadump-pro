# stories.py
import asyncio
import base64  # <--- EKSİK OLAN BUYDU
import os
import random
from playwright.async_api import Page

# --- İNDİRME FONKSİYONU ---
async def download_story_via_browser(page, url, username, media_type, prefix):
    try:
        if not url: return
        
        # 1. Veriyi Çek (JavaScript)
        base64_data = await page.evaluate(f"""async () => {{
            try {{
                const response = await fetch("{url}");
                if (!response.ok) return null;
                const blob = await response.blob();
                return new Promise((resolve) => {{
                    const reader = new FileReader();
                    reader.onloadend = () => resolve(reader.result);
                    reader.readAsDataURL(blob);
                }});
            }} catch(e) {{ return null; }}
        }}""")

        if not base64_data or "," not in base64_data: return

        # 2. Base64 Çöz
        header, encoded = base64_data.split(",", 1)
        binary_data = base64.b64decode(encoded)
        
        # 3. Klasöre Kaydet
        folder = f"downloads/{username}"
        os.makedirs(folder, exist_ok=True)
        
        ext = "mp4" if media_type == "video" else "jpg"
        filename = f"{folder}/{prefix}.{ext}"
        
        with open(filename, "wb") as f: 
            f.write(binary_data)
            
        print(f"   ✅ Story İndirildi: {prefix}.{ext}")
        
    except Exception as e: 
        print(f"   ❌ Story indirme hatası: {e}")

# --- ANA FONKSİYON ---
async def get_stories(page: Page, username: str):
    print(f"🟣 Story kontrol ediliyor: {username}")
    
    # --- DÜZELTME: ZORLA PROFİLE GİT ---
    await page.goto(f"https://www.instagram.com/{username}/")
    await page.wait_for_timeout(3000)
    
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(1)
    
    stories_data = {"has_active_story": False, "stories": []}

    try:
        # Profil resmini bul
        profile_pic_btn = await page.query_selector("header button:has(canvas), header a:has(canvas), header div[role='button']:has(canvas)")
        
        if not profile_pic_btn:
            # Halka yoksa story yok demektir, yine de resme tıklamayı deneyebiliriz ama genelde gerek yok.
            print("   -> Aktif story halkası (Canvas) bulunamadı.")
            return stories_data

        await profile_pic_btn.click(force=True)
        
        # URL değişimi bekle
        try:
            await page.wait_for_condition(lambda: "stories" in page.url, timeout=5000)
        except:
            # Açılmadıysa (Sadece resim büyüdüyse) kapat
            await page.keyboard.press("Escape")
            return stories_data

        print("   -> Story oynatıcı açıldı...")
        stories_data["has_active_story"] = True
        await asyncio.sleep(2)
        
        # Hata ekranı kontrolü
        page_content = await page.content()
        if "sorun yaşıyoruz" in page_content or "trouble playing" in page_content:
            print("   ⚠️ Siyah Ekran Hatası. Geçiliyor.")
            await page.goto(f"https://www.instagram.com/{username}/")
            return stories_data

        # Medya Bul
        try:
            await page.wait_for_selector("section video, section img", timeout=5000)
        except: pass

        # JavaScript ile en büyük medyayı bul
        media_info = await page.evaluate("""() => {
            // Video var mı?
            const video = document.querySelector('section video source') || document.querySelector('section video');
            if (video && video.src) return {type: 'video', src: video.src};

            // Resim var mı?
            const imgs = Array.from(document.querySelectorAll('section img'));
            // En büyük resmi bul (ikonları elemek için > 300px)
            const mainImg = imgs.find(img => img.naturalWidth > 300);
            
            if (mainImg) {
                let src = mainImg.src;
                if (mainImg.srcset) {
                    try { src = mainImg.srcset.split(',').pop().trim().split(' ')[0]; } catch(e){}
                }
                return {type: 'image', src: src};
            }
            return null;
        }""")
        
        if media_info and media_info['src']:
            prefix = f"story_{random.randint(1000,9999)}"
            
            # İndir
            await download_story_via_browser(page, media_info['src'], username, media_info['type'], prefix)
            
            stories_data["stories"].append({
                "type": media_info['type'], 
                "url": media_info['src']
            })
        
    except Exception as e:
        print(f"⚠️ Story hatası: {e}")

    # İşlem bitince profile dön
    if username not in page.url:
        await page.goto(f"https://www.instagram.com/{username}/")
        await asyncio.sleep(2)

    return stories_data