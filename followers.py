# followers.py
from playwright.async_api import Page
from utils.selectors import SELECTORS
import asyncio

async def scroll_and_collect(page: Page, limit: int, list_type: str):
    """
    Ortak scroll ve toplama fonksiyonu.
    list_type: 'followers' veya 'following'
    """
    target_link = f"a[href*='/{list_type}/']"
    
    try:
        # Linke tıkla
        await page.click(target_link)
        
        # Modalın (Pencerenin) açılmasını bekle
        # 'dialog' rolü Instagram'da değişmez, popup her zaman dialogdur.
        dialog = page.locator("div[role='dialog']")
        await dialog.wait_for(state="visible", timeout=5000)
        
    except Exception as e:
        print(f"⚠️ {list_type} listesi açılamadı: {e}")
        return []

    collected_names = set()
    print(f"   -> {list_type.capitalize()} listesi scroll ediliyor...")

    # Mouse'u dialog penceresinin üzerine getir (Scroll'un işlemesi için)
    box = await dialog.bounding_box()
    if box:
        await page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)

    # Scroll Döngüsü
    consecutive_no_new_names = 0
    
    while len(collected_names) < limit:
        # 1. Mevcut ekrandaki isimleri topla
        # Dialog içindeki, profil linki olan (href içeren) ama 'img' olmayan öğeleri alıyoruz
        elements = await page.locator("div[role='dialog'] a[href]:not(:has(img))").all()
        
        previous_count = len(collected_names)
        
        for el in elements:
            # Linkin içindeki metni (kullanıcı adı) al
            text = await el.inner_text()
            # Metni temizle (satır sonlarını vs at)
            clean_text = text.split('\n')[0].strip()
            
            if clean_text and clean_text != "Follow" and clean_text != "Takip Et":
                collected_names.add(clean_text)
        
        # Limit dolduysa çık
        if len(collected_names) >= limit:
            break

        # Yeni isim gelmediyse sayacı artır (Sonsuz döngüyü kırmak için)
        if len(collected_names) == previous_count:
            consecutive_no_new_names += 1
            if consecutive_no_new_names > 5: # 5 kere scroll yaptık yeni kimse gelmedi
                print("   -> Liste sonuna gelindi veya yeni veri yüklenmiyor.")
                break
        else:
            consecutive_no_new_names = 0

        # 2. Mouse Wheel ile Aşağı Kaydır (En Kritik Kısım)
        # Javascript kullanmıyoruz, fiziksel mouse hareketi taklit ediyoruz.
        await page.mouse.wheel(0, 500) 
        await page.wait_for_timeout(1000) # Yüklenmesi için bekle

    # Kapat
    await page.keyboard.press("Escape")
    await page.wait_for_timeout(1000)
    
    return list(collected_names)[:limit]

async def get_followers(page: Page, username: str, limit=50):
    print(f"👥 Takipçiler toplanıyor (Limit: {limit})...")
    # Profile gitmeyi garantiye al (eğer başka sayfadaysa)
    if username not in page.url:
        await page.goto(f"https://www.instagram.com/{username}/")
        await page.wait_for_timeout(2000)
        
    return await scroll_and_collect(page, limit, "followers")

async def get_following(page: Page, username: str, limit=50):
    print(f"b Takip edilenler toplanıyor (Limit: {limit})...")
    # Profile gitmeyi garantiye al
    if username not in page.url:
        await page.goto(f"https://www.instagram.com/{username}/")
        await page.wait_for_timeout(2000)

    return await scroll_and_collect(page, limit, "following")