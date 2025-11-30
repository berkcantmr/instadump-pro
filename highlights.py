# highlights.py
import asyncio
import random
import base64
import os
from playwright.async_api import Page
from tqdm import tqdm # <--- YENİ

# Browser Download Fonksiyonu (Sessizleştirdik - tqdm bozmasın diye)
async def download_via_browser(page, url, username, media_type, prefix):
    try:
        if not url: return
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

        header, encoded = base64_data.split(",", 1)
        binary_data = base64.b64decode(encoded)
        
        folder = f"downloads/{username}"
        os.makedirs(folder, exist_ok=True)
        ext = "mp4" if media_type == "video" else "jpg"
        filename = f"{folder}/{prefix}.{ext}"
        
        with open(filename, "wb") as f: f.write(binary_data)
        
        # tqdm.write(f"      ⬇️ İndirildi: {filename}") # Çok kalabalık olmasın diye kapattım
    except: pass

async def get_highlights(page: Page, username: str, dl_covers=True, dl_photos=True, dl_videos=True):
    print("\n🌟 Öne Çıkanlar (Highlights) taranıyor...")
    
    highlights_data = []
    
    try:
        await page.wait_for_selector("ul li a[href*='/stories/highlights/']", timeout=5000)
    except:
        print("   -> Öne çıkan hikaye bulunamadı.")
        return []

    highlight_queue = await page.evaluate("""() => {
        const links = Array.from(document.querySelectorAll("ul li a[href*='/stories/highlights/']"));
        return links.map(link => {
            const img = link.querySelector('img');
            let title = link.innerText.split('\\n')[0].trim();
            if (!title && img) title = img.alt;
            if (!title) title = 'Highlight';
            let coverUrl = img ? img.src : null;
            return { url: link.href, title: title, cover: coverUrl };
        });
    }""")

    total_count = len(highlight_queue)
    if total_count == 0: return []
    print(f"   -> {total_count} adet Albüm bulundu.")

    # Soru Sor
    try:
        limit_input = input(f"   ❓ Kaç albüm indirilsin? (Enter=Hepsi): ").strip()
        limit = int(limit_input) if limit_input else total_count
    except: limit = total_count

    if limit == 0: return []
    target_queue = highlight_queue[:limit]
    
    # --- PROGRESS BAR DÖNGÜSÜ ---
    # Albümleri tqdm ile dönüyoruz
    with tqdm(total=len(target_queue), desc="   📂 Albümler İşleniyor", unit="albüm", colour="cyan") as pbar:
        
        for index, hl in enumerate(target_queue):
            clean_title = "".join([c if c.isalnum() or c in (' ', '-', '_') else '' for c in hl['title']]).strip().replace(" ", "_")
            if len(clean_title) > 20: clean_title = clean_title[:20]
            if not clean_title: clean_title = f"HL_{index+1}"
            
            # Progress bar açıklamasını güncelle: "Albüm: Gezi"
            pbar.set_description(f"   📂 Albüm: {clean_title}")

            # Kapak
            if dl_covers and hl['cover']:
                await download_via_browser(page, hl['cover'], username, "image", f"cover_{clean_title}")

            if not dl_photos and not dl_videos:
                pbar.update(1)
                continue

            # İçerik İndirme
            album_id = hl['url'].split('/highlights/')[1].split('/')[0]

            try:
                await page.goto(hl['url'])
                await asyncio.sleep(2)
                
                # Bypass
                try:
                    bypass_btn = await page.query_selector("xpath=//*[contains(text(), 'Hikayeyi Gör')] | //*[contains(text(), 'View Story')]")
                    if bypass_btn: await page.evaluate("el => el.click()", bypass_btn)
                    if not await page.query_selector("section div"):
                        vp = page.viewport_size
                        if vp: await page.mouse.click(vp['width']/2, vp['height']/2 + 50)
                except: pass

                try:
                    await page.wait_for_selector("section div", timeout=8000)
                except:
                    pbar.update(1)
                    continue

                hl_media_count = 0
                seen_urls = set()
                empty_streak = 0 

                while True:
                    if album_id not in page.url: break
                    
                    media_info = await page.evaluate("""() => {
                        const video = document.querySelector('section video source') || document.querySelector('section video');
                        if (video && video.src) return {type: 'video', src: video.src};
                        
                        const imgs = Array.from(document.querySelectorAll('section img'));
                        const bigImgs = imgs.filter(img => img.naturalWidth > 300);
                        const mainImg = bigImgs.find(img => img.sizes || img.srcset || img.className.includes('x5yr21d'));
                        const targetImg = mainImg || (bigImgs.length > 0 ? bigImgs[0] : null);
                        
                        if (targetImg) {
                            let src = targetImg.src;
                            if (targetImg.srcset) {
                                try { src = targetImg.srcset.split(',').pop().trim().split(' ')[0]; } catch(e){}
                            }
                            return {type: 'image', src: src};
                        }
                        return null;
                    }""")

                    if media_info and media_info['src']:
                        src = media_info['src']
                        media_type = media_info['type']
                        empty_streak = 0
                        
                        should_dl = (media_type == 'video' and dl_videos) or (media_type == 'image' and dl_photos)
                        
                        if not should_dl:
                            if src not in seen_urls: seen_urls.add(src)
                        elif src in seen_urls:
                            pass
                        else:
                            seen_urls.add(src)
                            hl_media_count += 1
                            prefix = f"highlight_{clean_title}_{hl_media_count}"
                            await download_via_browser(page, src, username, media_type, prefix)
                    else:
                        has_error = await page.evaluate("""() => {
                            const text = document.body.innerText;
                            return text.includes("video oynatılamıyor") || text.includes("oynatmada sorun");
                        }""")
                        if has_error:
                            await page.keyboard.press("ArrowRight")
                            await asyncio.sleep(1)
                            continue

                        empty_streak += 1
                        if empty_streak > 5: break

                    await page.keyboard.press("ArrowRight")
                    wait_time = 3.5 if media_info and media_info['type'] == 'video' and dl_videos else 1.5
                    await asyncio.sleep(wait_time)
                    if username in page.url and "highlights" not in page.url: break

                highlights_data.append({"title": hl['title'], "count": hl_media_count, "url": hl['url']})

            except: pass
            
            pbar.update(1) # Albüm bitti, çubuğu ilerlet

    if username not in page.url:
        await page.goto(f"https://www.instagram.com/{username}/")
        
    return highlights_data