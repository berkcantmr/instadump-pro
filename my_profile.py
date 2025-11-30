# my_profile.py (Eski adı profile.py idi)
import asyncio
import base64
import os
from playwright.async_api import Page
from utils.selectors import SELECTORS

# --- YARDIMCI İNDİRME FONKSİYONU ---
async def download_pp_via_browser(page, url, username):
    """Profil resmini tarayıcı hafızasından indirir"""
    if not url: return None
    
    try:
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

        if not base64_data or "," not in base64_data:
            return None

        header, encoded = base64_data.split(",", 1)
        binary_data = base64.b64decode(encoded)
        
        folder = f"downloads/{username}"
        os.makedirs(folder, exist_ok=True)
        
        filename = f"{folder}/profile_pic_{username}.jpg"
        
        with open(filename, "wb") as f:
            f.write(binary_data)
            
        print(f"   🖼️ Profil resmi indirildi: {filename}")
        return filename

    except Exception as e:
        print(f"   ⚠️ Profil resmi indirilemedi: {e}")
        return None

async def get_profile_info(page: Page, target_username: str):
    print(f"🔍 {target_username} profili taranıyor...")
    
    if target_username not in page.url:
        await page.goto(f"https://www.instagram.com/{target_username}/")
    
    try:
        await page.wait_for_selector(SELECTORS["profile_check"], timeout=8000)
    except:
        print("❌ Profil yüklenemedi (Sayfa yok veya internet yavaş).")
        return None

    profile_data = {
        "username": target_username,
        "is_private": False,
        "is_following": False,
        "profile_pic_local": None
    }

    # Gizlilik Kontrolü
    try:
        page_content = await page.content()
        if "Bu hesap gizli" in page_content or "This account is private" in page_content:
            profile_data["is_private"] = True
            print(f"   🔒 {target_username} hesabı GİZLİ.")
    except: pass

    # Profil Resmi
    try:
        img_element = await page.query_selector(SELECTORS["profile_img"])
        pp_url = await img_element.get_attribute("src") if img_element else None
        
        if pp_url:
            profile_data["profile_pic_url"] = pp_url
            local_path = await download_pp_via_browser(page, pp_url, target_username)
            profile_data["profile_pic_local"] = local_path
            
    except Exception as e: 
        print(f"   ⚠️ PP hatası: {e}")
        profile_data["profile_pic_url"] = None

    # Bio
    try:
        bio_element = await page.query_selector("h1 + div") or await page.query_selector("div.-vDIg span") or await page.query_selector("div._aacl._aaco._aacu._aacx._aad7._aade")
        profile_data["bio"] = await bio_element.inner_text() if bio_element else ""
    except: profile_data["bio"] = ""

    # Sayılar
    try:
        followers_el = await page.query_selector(SELECTORS["followers_link"])
        following_el = await page.query_selector(SELECTORS["following_link"])
        
        if followers_el:
            profile_data["followers_count"] = await followers_el.get_attribute("title") or await followers_el.inner_text()
        else:
            spans = await page.query_selector_all("ul li span")
            if len(spans) >= 2:
                profile_data["followers_count"] = await spans[1].get_attribute("title") or await spans[1].inner_text()
            else:
                profile_data["followers_count"] = "-"

        profile_data["following_count"] = await following_el.inner_text() if following_el else "-"
    except Exception as e:
        profile_data["followers_count"] = "-"
        profile_data["following_count"] = "-"
        
    return profile_data