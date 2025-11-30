# utils/selectors.py

SELECTORS = {
    "login_check": "svg[aria-label='Home'], svg[aria-label='Ana Sayfa']",
    "profile_check": "header section",
    "private_account_text": "h2", 
    "private_text_keywords": ["This account is private", "Bu hesap gizli"],
    "profile_img": "header img",
    "followers_link": "a[href*='/followers/']",
    "following_link": "a[href*='/following/']",
    "post_link": "main a[href^='/p/']", 
    "modal_dialog": "div[role='dialog']",
    "user_list_item": "div[role='dialog'] a[href] div div",
    
    # YENİ: Highlights (Öne Çıkanlar)
    # Profilin altında, story halkalarına benzeyen alan
    "highlights_container": "ul.x78zum5.x1q0g3np.x1a02dak.x1qughib", 
    "highlight_item": "li.x1i10hfl", 
}