# login.py
import os
import asyncio
from playwright.async_api import Page
from utils.selectors import SELECTORS

async def perform_login(page: Page, session_path: str):
    """
    Belirtilen session_path'i kullanarak giriş yapar veya kaydeder.
    """
    print(f"🔵 Oturum dosyası kontrol ediliyor: {session_path}")
    
    # Session klasörünün var olduğundan emin ol
    os.makedirs(os.path.dirname(session_path), exist_ok=True)
    
    await page.goto("https://www.instagram.com/")
    await page.wait_for_timeout(3000)

    # 1. ZATEN GİRİŞ YAPILI MI?
    try:
        # Home ikonu veya Profil resmi var mı?
        if await page.query_selector(SELECTORS["login_check"]) or await page.query_selector("header img"):
            print("✅ Kayıtlı oturum geçerli! Giriş ekranı atlanıyor.")
            # Oturumu tazele
            await page.context.storage_state(path=session_path)
            return
    except:
        pass

    # 2. DEĞİLSE MANUEL GİRİŞ İSTE
    print("\n" + "="*50)
    print(f"⚠️  '{os.path.basename(session_path)}' İÇİN OTURUM AÇIK DEĞİL.")
    print("👉 Lütfen tarayıcıdan giriş yapın (Şifre/2FA).")
    print("✅  Giriş yapıp ANASAYFAYI görünce buraya gelip ENTER'a basın.")
    print("="*50 + "\n")
    
    await asyncio.get_event_loop().run_in_executor(None, input, "Giriş tamamlandıysa ENTER'a bas...")
    
    # 3. KAYDET
    try:
        if await page.query_selector(SELECTORS["login_check"]) or await page.query_selector("header img"):
            print(f"✅ Giriş başarılı! Oturum şuraya kaydediliyor: {session_path}")
            await page.context.storage_state(path=session_path)
        else:
            print("⚠️ Uyarı: Ana sayfa tam algılanamadı ama devam ediliyor.")
            await page.context.storage_state(path=session_path)
            
    except Exception as e:
        print(f"❌ Oturum kaydetme hatası: {e}")
    
    await page.wait_for_timeout(2000)