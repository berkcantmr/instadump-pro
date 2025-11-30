import asyncio
import os
import glob
import random
import shutil
import time
from playwright.async_api import async_playwright, Error as PlaywrightError

# --- MODÜL İMPORTLARI ---
# (Dosya adlarının doğru olduğundan emin ol: my_profile.py, login.py vb.)
from login import perform_login 
from my_profile import get_profile_info
from posts import get_posts
from followers import get_followers, get_following
from stories import get_stories
from highlights import get_highlights
from utils.save_json import save_data

# ==========================================
# GÖRSELLEŞTİRME VE EKRAN YÖNETİMİ
# ==========================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner(status_lines=None):
    clear_screen()
    # Cyan Rengi
    banner = r"""
██╗███╗   ██╗███████╗████████╗ █████╗ ██████╗ ██╗   ██╗███╗   ███╗██████╗     ██████╗ ██████╗  ██████╗ 
██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║   ██║████╗ ████║██╔══██╗    ██╔══██╗██╔══██╗██╔═══██╗
██║██╔██╗ ██║███████╗   ██║   ███████║██║  ██║██║   ██║██╔████╔██║██████╔╝    ██████╔╝██████╔╝██║   ██║
██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║  ██║██║   ██║██║╚██╔╝██║██╔═══╝     ██╔═══╝ ██╔══██╗██║   ██║
██║██║ ╚████║███████║   ██║   ██║  ██║██████╔╝╚██████╔╝██║ ╚═╝ ██║██║         ██║     ██║  ██║╚██████╔╝
╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝         ╚═╝     ╚═╝  ╚═╝ ╚═════╝ 
    """
    print(f"\033[96m{banner}\033[0m")
    print(f"\033[93m   🔥 Ultimate Instagram Archiving & Analysis Tool | v6.4 CrashGuard Edition\033[0m")
    print(f"\033[90m   " + "="*95 + "\033[0m")
    
    if status_lines:
        print("\n\033[92m✅ DURUM:\033[0m")
        for line in status_lines:
            print(f"   └─ {line}")
        print(f"\033[90m   " + "-"*30 + "\033[0m\n")

def print_red_alert():
    clear_screen()
    red = "\033[91m"
    reset = "\033[0m"
    
    warning_header = r"""
$$\   $$\ $$\     $$\  $$$$$$\  $$$$$$$\  $$$$$$\ 
$$ |  $$ |\$$\   /  |$$  __$$\ $$  __$$\ \_$$  _|
$$ |  $$ | \$$\ /  / $$ /  $$ |$$ |  $$ |  $$ |  
$$ |  $$ |  \$$\  /  $$$$$$$$ |$$$$$$$  |  $$ |  
$$ |  $$ |   \$$ /   $$  __$$ |$$  __$$<   $$ |  
$$ |  $$ |    $$ |   $$ |  $$ |$$ |  $$ |  $$ |  
\$$$$$$  |    $$ |   $$ |  $$ |$$ |  $$ |$$$$$$\ 
 \______/     \__|   \__|  \__|\__|  \__|\______|
    """
    options_art = r"""
      [ SİLMEK İÇİN: 'EVET' ]           [ İPTAL İÇİN: 'HAYIR' ]
    """
    print(f"{red}{warning_header}{reset}")
    print(f"{red}" + "="*80 + f"{reset}")
    print(f"{red}   ⚠️  DİKKAT: BU İŞLEM GERİ ALINAMAZ! TÜM VERİLER SİLİNECEK.{reset}")
    print(f"{red}" + "="*80 + f"{reset}")
    print(f"{red}{options_art}{reset}")
    print("\n")

def print_crash_screen(error_msg):
    clear_screen()
    red = "\033[91m"
    reset = "\033[0m"
    yellow = "\033[93m"
    
    crash_art = r"""
      _____ _____            _____ _    _ 
     / ____|  __ \     /\   / ____| |  | |
    | |    | |__) |   /  \ | (___ | |__| |
    | |    |  _  /   / /\ \ \___ \|  __  |
    | |____| | \ \  / ____ \____) | |  | |
     \_____|_|  \_\/_/    \_\_____/|_|  |_|
    """
    print(f"{red}{crash_art}{reset}")
    print(f"{red}" + "="*60 + f"{reset}")
    print(f"{yellow}   ⚠️  UYGULAMA BEKLENMEDİK ŞEKİLDE DURDURULDU!{reset}")
    print(f"{red}   HATA: {error_msg}{reset}")
    print(f"{red}" + "="*60 + f"{reset}\n")

# ==========================================
# DOSYA VE SESSION YÖNETİMİ
# ==========================================

def manage_existing_dumps():
    output_dir = "output"
    downloads_dir = "downloads"
    
    if not os.path.exists(output_dir): return
    files = glob.glob(os.path.join(output_dir, "*.json"))
    if not files: return

    print("\n📂 --- MEVCUT DUMP KAYITLARI ---")
    file_map = {}
    for i, f in enumerate(files):
        username = os.path.basename(f).replace(".json", "")
        file_map[str(i+1)] = username
        print(f"   [{i+1}] {username}")

    print("\n⬇️ --- DUMP YÖNETİMİ ---")
    ask = input("❓ Mevcut kayıtları silmek ister misiniz? [e/H]: ").lower()
    
    if ask == 'e':
        print("\n   [ID] Numaralı kullanıcıyı sil")
        print("   [A]  TÜMÜNÜ SİL (Format At)")
        print("   [X]  İptal / Devam Et")
        
        choice = input("   👉 Seçiminiz: ").strip().lower()
        
        if choice in file_map:
            user_to_delete = file_map[choice]
            json_path = os.path.join(output_dir, f"{user_to_delete}.json")
            if os.path.exists(json_path): os.remove(json_path)
            folder_path = os.path.join(downloads_dir, user_to_delete)
            if os.path.exists(folder_path): shutil.rmtree(folder_path)
            
            print(f"   🗑️  {user_to_delete} verileri temizlendi.")
            time.sleep(1.5)
            
        elif choice == 'a':
            print_red_alert()
            confirm = input("   ❓ Kararınız (EVET / HAYIR): ").strip().upper()
            
            if confirm == "EVET":
                print("\n   🔥 İmha işlemi başlatılıyor...")
                time.sleep(1)
                for f in files:
                    try: os.remove(f)
                    except: pass
                    u_name = os.path.basename(f).replace(".json", "")
                    d_path = os.path.join(downloads_dir, u_name)
                    if os.path.exists(d_path): shutil.rmtree(d_path)
                print("   ☠️  Tüm arşiv başarıyla silindi.")
                time.sleep(2)
            else:
                print("\n   🛡️  İşlem iptal edildi.")
                time.sleep(1)
    
    # İşlem bitince temizle
    print_banner()

def get_session_choice():
    session_dir = "sessions"
    os.makedirs(session_dir, exist_ok=True)
    files = glob.glob(os.path.join(session_dir, "*.json"))
    
    print("🔐 --- AKTİF OTURUMLAR ---")
    if not files:
        print("   (Henüz kayıtlı oturum yok)")
        print("   [1] Yeni Oturum Oluştur")
        choice = "1"
    else:
        for i, f in enumerate(files):
            name = os.path.basename(f).replace(".json", "")
            print(f"   [{i+1}] {name}")
        print(f"   [{len(files)+1}] + Yeni Oturum Ekle")
        choice = input("\n👉 Seçiminiz: ").strip()

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(files):
            path = files[idx]
            name = os.path.basename(path).replace(".json", "")
            return path, name
    
    print("\n🆕 Yeni oturum oluşturuluyor...")
    new_name = input("👉 Yeni oturum adı (Örn: kullaniciadim): ").strip() or "default_session"
    return os.path.join(session_dir, f"{new_name}.json"), new_name

# ==========================================
# İŞLEM MANTIĞI (CORE LOGIC)
# ==========================================

async def process_single_user(page, username, config):
    print(f"\n⚡ --- {username} İŞLENİYOR ---")
    filename = f"output/{username}.json"
    profile_url = f"https://www.instagram.com/{username}/"

    try:
        # 1. PROFİL (Her zaman ana sayfaya git)
        await page.goto(profile_url)
        await asyncio.sleep(2)
        
        profile_data = await get_profile_info(page, username)
        if not profile_data: 
            print("❌ Profil açılamadı.")
            return
        
        is_private = profile_data.get('is_private')
        if is_private: print(f"🔒 {username} gizli hesap.")
        save_data({"profile": profile_data}, filename)

        # 2. NETWORK
        if config['dl_network'] and not is_private:
            print("   👥 Network analizi...")
            await page.goto(profile_url) # Reset
            followers = await get_followers(page, username, limit=50)
            following = await get_following(page, username, limit=50)
            save_data({"network": {"followers": followers, "following": following}}, filename)

        # 3. POST
        if config['dl_posts'] and not is_private:
            await page.goto(profile_url) # Reset
            await asyncio.sleep(2)
            posts_data = await get_posts(page, username, limit=config['limit_post'])
            save_data({"posts": posts_data}, filename)
        
        # 4. HIGHLIGHTS
        if config['dl_hl_covers'] or config['dl_hl_photos'] or config['dl_hl_videos']:
            await page.goto(profile_url) # Reset
            await asyncio.sleep(2)
            hl_data = await get_highlights(
                page, username, 
                dl_covers=config['dl_hl_covers'], 
                dl_photos=config['dl_hl_photos'], 
                dl_videos=config['dl_hl_videos']
            )
            save_data({"highlights": hl_data}, filename)

        # 5. STORY
        if config['dl_stories']:
            await page.goto(profile_url) # Reset
            await asyncio.sleep(2)
            st_data = await get_stories(page, username)
            save_data({"stories": st_data}, filename)

    except Exception as e:
        # Hatayı fırlat ki ana döngü yakalasın
        raise e

async def run_browser_task(session_path, my_username, target_users, config, mode_choice, list_type, limit_user):
    """
    Tarayıcıyı başlatıp görevleri yapan izole fonksiyon.
    """
    async with async_playwright() as p:
        # STEALTH AYARLARI
        REAL_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        browser = await p.chromium.launch(
            headless=False, 
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
        )
        
        context_args = {
            "user_agent": REAL_USER_AGENT,
            "viewport": {"width": 1366, "height": 768},
            "locale": "tr-TR"
        }
        
        if os.path.exists(session_path):
            try:
                context = await browser.new_context(storage_state=session_path, **context_args)
            except:
                context = await browser.new_context(**context_args)
        else:
            context = await browser.new_context(**context_args)

        # Webdriver gizleme
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        await perform_login(page, session_path)
        
        # Liste moduysa listeyi burada çek (restart durumunda liste kaybolmasın diye)
        current_targets = target_users
        if mode_choice != "1" and not current_targets:
            print(f"\n📋 Liste toplanıyor ({list_type})...")
            if list_type == "following":
                current_targets = await get_following(page, my_username, limit_user)
            else:
                current_targets = await get_followers(page, my_username, limit_user)
        
        if current_targets:
            print(f"\n✅ Toplam {len(current_targets)} hedef işlenecek.")
            for i, user in enumerate(current_targets):
                print(f"\n[{i+1}/{len(current_targets)}]")
                await process_single_user(page, user, config)
                if len(current_targets) > 1: await asyncio.sleep(random.randint(3, 6))

        return True

# ==========================================
# ANA DÖNGÜ (MAIN LOOP)
# ==========================================

async def main():
    # 1. BAŞLANGIÇ AYARLARI
    print_banner()
    manage_existing_dumps() # Silme işlemi burada
    
    session_path, session_name = get_session_choice()
    status = [f"Aktif Hesap: {session_name}"]
    print_banner(status)

    my_username = input("👉 Sizin Kullanıcı Adınız (Değişmeyecekse Enter): ").strip()
    if not my_username: my_username = session_name

    # 2. HEDEF BELİRLEME
    print_banner(status)
    print("🎯 --- HEDEF SEÇİMİ ---")
    print("   [1] Özel Bir Kullanıcıyı Tara")
    print("   [2] Benim Listemi Tara")
    mode_choice = input("   👉 Seçiminiz: ").strip()

    target_users = []
    list_type = "following"
    limit_user = 50
    mode_desc = ""
    
    if mode_choice == "1":
        target = input("   👉 Hedef Kullanıcı Adı: ").strip()
        target_users = [target]
        mode_desc = f"Tekil Hedef ({target})"
    else:
        ttype = input("   👉 [1] Takip Ettiklerim / [2] Takipçilerim: ").strip()
        list_type = "following" if ttype == "1" else "followers"
        limit_user = int(input("   👉 Kaç KİŞİ taransın? (Enter=50): ").strip() or 50)
        mode_desc = f"Toplu Tarama ({list_type} - {limit_user} kişi)"

    status.append(f"Mod: {mode_desc}")

    # 3. İNDİRME AYARLARI
    print_banner(status)
    print("⬇️ --- İNDİRME AYARLARI (E=Evet / H=Hayır) ---")
    def ask(msg): return input(f"❓ {msg} [E/h]: ").lower() not in ['h', 'hayır', 'n']

    config = {
        'dl_network':    ask("Network analizi?"),
        'dl_posts':      ask("Postlar indirilsin mi?"),
        'dl_hl_covers':  ask("Highlight KAPAKLARI?"),
        'dl_hl_photos':  ask("Highlight FOTOĞRAFLARI?"),
        'dl_hl_videos':  ask("Highlight VİDEOLARI?"),
        'dl_stories':    ask("Storyler?"),
        'limit_post':    10
    }
    if config['dl_posts']:
        config['limit_post'] = int(input("   👉 Kişi başı max kaç POST? (Enter=10): ").strip() or 10)

    # 4. SONSUZ DÖNGÜ (CRASH KORUMASI)
    while True:
        print_banner(status)
        print("\n🚀 Tarayıcı başlatılıyor, işlemler yapılıyor...")
        
        try:
            # Tarayıcıyı Başlat
            is_completed = await run_browser_task(
                session_path, my_username, target_users, config, mode_choice, list_type, limit_user
            )
            
            if is_completed:
                print("\n✅ TÜM İŞLEMLER BAŞARIYLA TAMAMLANDI.")
                input("🔴 Çıkmak için ENTER tuşuna basın...")
                break 

        except Exception as e:
            # HATA EKRANI
            error_msg = str(e)
            print_crash_screen(error_msg)
            
            retry = input("   🔄 İşlemleri baştan başlatmak ister misiniz? [E/h]: ").lower()
            if retry in ['h', 'hayır', 'n']:
                print("   ❌ Çıkış yapılıyor...")
                break
            else:
                print("   ♻️  Yeniden başlatılıyor...")
                time.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())