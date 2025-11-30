# posts.py
import asyncio
import random
from playwright.async_api import Page
from utils.downloader import download_file
from tqdm import tqdm # <--- YENİ KÜTÜPHANE

async def get_posts(page: Page, username: str, limit=20): 
    print(f"\n📸 Postlar taranıyor (Hedef: {limit} adet)...")
    
    # --- 1. LİNKLERİ TOPLA ---
    print("   -> Sayfa aşağı kaydırılıyor, linkler toplanıyor (Bu işlem biraz sürebilir)...")
    
    post_urls = set()
    no_new_data_count = 0
    
    await page.wait_for_timeout(3000)

    # Link toplama sırasında basit bir spinner/sayaç gösterelim
    pbar_collect = tqdm(total=limit, desc="   🔗 Link Bulundu", unit="link", bar_format="{desc}: {n_fmt}")
    
    while len(post_urls) < limit:
        current_urls = await page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a'));
            return links.map(link => link.href).filter(href => href.includes('/p/') || href.includes('/reel/'));
        }""")
        
        prev_len = len(post_urls)
        for url in current_urls:
            if url not in post_urls:
                post_urls.add(url)
                pbar_collect.update(1) # Sayacı artır
        
        if len(post_urls) == prev_len:
            no_new_data_count += 1
            if no_new_data_count > 3: break
        else:
            no_new_data_count = 0

        await page.mouse.wheel(0, 4000)
        await asyncio.sleep(2.5)
        
        if len(post_urls) >= limit: break
    
    pbar_collect.close()
    final_urls = list(post_urls)[:limit]
    posts_data = []

    if not final_urls:
        print("❌ HİÇ POST LİNKİ BULUNAMADI!")
        return []

    print(f"   -> Toplam {len(final_urls)} post indirilecek.")

    # --- 2. İNDİRME DÖNGÜSÜ (PROGRESS BAR BURADA) ---
    # tqdm ile döngüyü sarıyoruz
    for full_url in tqdm(final_urls, desc="   💾 İndiriliyor", unit="post", colour="green"):
        try:
            await page.goto(full_url)
            
            try:
                await page.wait_for_selector("img[sizes], video, main img", timeout=15000)
            except:
                pass # Zaman aşımı olsa bile dene

            seen_media = set()
            slide_count = 0
            
            while True:
                slide_count += 1
                
                # Medya Bul
                media_info = await page.evaluate("""() => {
                    const video = document.querySelector('video');
                    if (video && video.src) return {type: 'video', src: video.src};
                    
                    const imgs = Array.from(document.querySelectorAll('img'));
                    const mainImg = imgs.find(img => img.hasAttribute('sizes') || img.style.objectFit || img.className.includes('x5yr21d'));
                    
                    if (mainImg) {
                        let src = mainImg.src;
                        if (mainImg.srcset) src = mainImg.srcset.split(',').pop().trim().split(' ')[0];
                        return {type: 'image', src: src};
                    }
                    if (imgs.length > 0) return {type: 'image', src: imgs[1] ? imgs[1].src : imgs[0].src};
                    return null;
                }""")
                
                if media_info and media_info['src']:
                    src = media_info['src']
                    if not src.startswith("blob:") and src not in seen_media:
                        seen_media.add(src)
                        try:
                            post_id = full_url.split('/p/')[-1].split('/')[0]
                        except: post_id = f"unknown_{random.randint(1000,9999)}"
                        
                        prefix = f"post_{post_id}_{slide_count}"
                        
                        # tqdm kullanırken print yerine tqdm.write kullanılır (satır kaymaması için)
                        # download_file(src, username, media_info['type'], prefix=prefix)
                        # Ama biz download_file'ı sessiz modda çalıştırmadık, o yüzden loglar karışabilir.
                        # En temizi sessizce indirmektir.
                        download_file(src, username, media_info['type'], prefix=prefix)
                
                # Sonraki Slayt
                has_next = await page.evaluate("""() => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const nextBtn = buttons.find(b => b.getAttribute('aria-label') === 'Next' || b.getAttribute('aria-label') === 'İleri');
                    if (nextBtn) { nextBtn.click(); return true; }
                    return false;
                }""")
                
                if has_next: await asyncio.sleep(2)
                else: break 

            posts_data.append({"url": full_url, "media": list(seen_media)})
            await asyncio.sleep(random.uniform(2, 4))

        except Exception as e:
            tqdm.write(f"      ⚠️ Hata: {e}")

    return posts_data