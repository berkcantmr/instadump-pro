import streamlit as st
import json
import os
import glob
import pandas as pd
from PIL import Image

# Sayfa Ayarları
st.set_page_config(page_title="Instagram Dump Viewer v6.2", page_icon="📂", layout="wide")

# CSS: Arayüzü Güzelleştir
st.markdown("""
<style>
    .stMetric {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 10px;
        border-radius: 8px;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #333;
        border-radius: 8px;
    }
    /* Kırık resim ikonlarını gizle */
    img[alt="image"] {
        color: transparent; 
    }
</style>
""", unsafe_allow_html=True)

st.title("📂 Instagram Arşiv Görüntüleyici")

# --- YAN MENÜ ---
st.sidebar.header("📁 Arşiv Seçimi")
output_dir = "output"
downloads_base_dir = "downloads"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

json_files = glob.glob(os.path.join(output_dir, "*.json"))
if not json_files:
    st.warning("⚠️ Veri bulunamadı. Lütfen önce tarama yapın.")
    st.stop()

file_options = {os.path.basename(f).replace(".json", ""): f for f in json_files}
selected_user = st.sidebar.selectbox("Kullanıcı Seçin:", list(file_options.keys()))

# --- VERİ YÜKLEME ---
selected_path = file_options[selected_user]
try:
    with open(selected_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    st.error("Veri dosyası bozuk.")
    st.stop()

# --- 1. PROFİL KARTI ---
st.markdown("---")
col1, col2 = st.columns([1, 4])

with col1:
    local_pp_path = f"{downloads_base_dir}/{selected_user}/profile_pic_{selected_user}.jpg"
    json_pp_path = data.get('profile', {}).get('profile_pic_local')

    if os.path.exists(local_pp_path):
        st.image(local_pp_path, width=150)
    elif json_pp_path and os.path.exists(json_pp_path):
        st.image(json_pp_path, width=150)
    elif data.get('profile', {}).get('profile_pic_url'):
        try:
            st.image(data['profile']['profile_pic_url'], width=150)
        except:
            st.markdown("## 👤")
    else:
        st.markdown("## 👤")

with col2:
    p_data = data.get('profile', {})
    username = p_data.get('username', selected_user)
    st.subheader(f"@{username}")
    
    bio = p_data.get('bio', '')
    if bio: st.info(bio)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Takipçi", p_data.get('followers_count', '-'))
    m2.metric("Takip", p_data.get('following_count', '-'))
    
    user_path = os.path.join(downloads_base_dir, selected_user)
    f_count = len([n for n in os.listdir(user_path)]) if os.path.exists(user_path) else 0
    m3.metric("Toplam Dosya", f_count)
    
    is_private = p_data.get('is_private', False)
    m4.metric("Durum", "🔒 Gizli" if is_private else "🔓 Açık")

# --- SEKMELER ---
tab1, tab2, tab3, tab4 = st.tabs(["📂 GALERİ", "👥 Network Analizi", "🟣 Story & Highlight", "📸 Linkler"])

# --- TAB 1: GALERİ ---
with tab1:
    if os.path.exists(user_path):
        files = sorted(os.listdir(user_path), reverse=True)
        files = [f for f in files if not f.startswith("profile_pic")]
        
        imgs = [f for f in files if f.endswith(('.jpg','.png'))]
        vids = [f for f in files if f.endswith('.mp4')]
        
        ftype = st.radio("Filtre:", ["Tümü", "Foto", "Video"], horizontal=True, label_visibility="collapsed")
        
        show_list = files
        if ftype == "Foto": show_list = imgs
        elif ftype == "Video": show_list = vids
        
        if show_list:
            cols = st.columns(4)
            for i, f in enumerate(show_list):
                path = os.path.join(user_path, f)
                with cols[i%4]:
                    if f.endswith('.mp4'):
                        st.video(path)
                    else:
                        # use_container_width yerine width="stretch"
                        st.image(path, width="stretch")
                    st.caption(f, unsafe_allow_html=False)
        else:
            st.info("Bu kategoride dosya yok.")
    else:
        st.warning("Henüz indirilmiş dosya yok.")

# --- TAB 2: NETWORK ANALİZİ ---
with tab2:
    network = data.get('network', {})
    
    if not network:
        st.info("⚠️ Bu kullanıcı için Network analizi yapılmamış.")
    else:
        followers = network.get('followers', [])
        following = network.get('following', [])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplanan Takipçi", len(followers))
        c2.metric("Toplanan Takip Edilen", len(following))
        mutuals = list(set(followers) & set(following))
        c3.metric("🤝 Karşılıklı Takipleşme", len(mutuals))
        
        st.divider()
        
        net_tab1, net_tab2, net_tab3 = st.tabs(["Takipçiler", "Takip Edilenler", "🤝 Mutual"])
        
        # --- DÜZELTME BURADA YAPILDI ---
        # st.dataframe içindeki parametreler güncellendi
        
        with net_tab1:
            if followers:
                df_f = pd.DataFrame(followers, columns=["Kullanıcı Adı"])
                # use_container_width=True  --->  width="stretch" (veya kaldırıldı)
                # Not: Dataframe uyarısı 'width' parametresi istiyorsa:
                try:
                    st.dataframe(df_f, use_container_width=True, height=500)
                except:
                    # Eğer sürüm çok yeniyse ve use_container_width kalktıysa
                    st.dataframe(df_f, height=500)
            else: st.write("Boş.")
        
        with net_tab2:
            if following:
                df_fol = pd.DataFrame(following, columns=["Kullanıcı Adı"])
                try:
                    st.dataframe(df_fol, use_container_width=True, height=500)
                except:
                    st.dataframe(df_fol, height=500)
            else: st.write("Boş.")

        with net_tab3:
            if mutuals:
                st.success(f"{len(mutuals)} kişi karşılıklı takipleşiyor.")
                df_mut = pd.DataFrame(mutuals, columns=["Karşılıklı Takip"])
                try:
                    st.dataframe(df_mut, use_container_width=True, height=500)
                except:
                    st.dataframe(df_mut, height=500)
            else: st.warning("Yok.")

# --- TAB 3: STORY ---
with tab3:
    stories = data.get('stories', {}).get('stories', [])
    highlights = data.get('highlights', [])
    
    if not stories and not highlights:
        st.info("Hikaye verisi yok.")
    
    if stories:
        st.markdown("#### 🟣 24 Saatlik Hikayeler")
        cols = st.columns(4)
        for i, s in enumerate(stories):
            with cols[i%4]:
                if s.get('local_path') and os.path.exists(s['local_path']):
                    if s['type']=='image':
                        st.image(s['local_path'], width="stretch")
                    else:
                        st.video(s['local_path'])
                    st.caption("✅ İndirildi")
                else:
                    st.write(f"🔗 [Link]({s['url']})")

    if highlights:
        st.markdown("#### 🌟 Öne Çıkanlar")
        for hl in highlights:
            with st.expander(f"{hl.get('title','Highlight')} ({hl.get('count',0)} medya)"):
                st.write(f"Link: {hl.get('url')}")

# --- TAB 4: POST LINKLERI ---
with tab4:
    posts = data.get('posts', [])
    if posts:
        for i, p in enumerate(posts):
            st.markdown(f"**Post {i+1}:** {p.get('url')}")
            if 'media' in p:
                st.caption(f"{len(p['media'])} parça içerik")
            st.divider()
    else:
        st.info("Post linki yok.")

if st.sidebar.button("📂 Klasörü Aç"):
    try: os.startfile(user_path)
    except: st.sidebar.error("Açılamadı.")