import streamlit as st
import hashlib
import json
import datetime
from PIL import Image, ImageDraw
import imagehash
import qrcode
from io import BytesIO

st.set_page_config(page_title="ArtGuard AI", page_icon="🎨", layout="wide")

st.markdown("""
    <style>
    /* Genel Arka Plan */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Ana İçerik */
    .main .block-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    
    /* Başlıklar */
    h1 {
        background: linear-gradient(120deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        color: #2c3e50;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
    }
    
    h3 {
        color: #34495e;
    }
    
    /* Butonlar */
    .stButton > button {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
        color: white !important;
        border-radius: 25px !important;
        padding: 0.7rem 2rem !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Metrikler */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: bold !important;
        color: #667eea !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #7f8c8d !important;
    }
    
    /* Uyarı Kutuları */
    .stSuccess {
        background-color: #d4edda !important;
        border-left: 5px solid #28a745 !important;
        padding: 1rem !important;
        border-radius: 5px !important;
    }
    
    .stError {
        background-color: #f8d7da !important;
        border-left: 5px solid #dc3545 !important;
        padding: 1rem !important;
        border-radius: 5px !important;
    }
    
    .stWarning {
        background-color: #fff3cd !important;
        border-left: 5px solid #ffc107 !important;
        padding: 1rem !important;
        border-radius: 5px !important;
    }
    
    .stInfo {
        background-color: #d1ecf1 !important;
        border-left: 5px solid #17a2b8 !important;
        padding: 1rem !important;
        border-radius: 5px !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8f9fa !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        color: #2c3e50 !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }
    
    /* Input alanları */
    .stTextInput > div > div > input {
        border-radius: 10px !important;
        border: 2px solid #e0e0e0 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25) !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #f8f9fa;
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
    }
    
    /* Code blocks */
    code {
        background: #f4f4f4 !important;
        padding: 0.3rem 0.6rem !important;
        border-radius: 5px !important;
        color: #667eea !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

if 'zincir' not in st.session_state:
    st.session_state.zincir = []
if 'hashler' not in st.session_state:
    st.session_state.hashler = set()
if 'resim_hashler' not in st.session_state:
    st.session_state.resim_hashler = []
if 'ai_sayac' not in st.session_state:
    st.session_state.ai_sayac = 0
if 'transfer_sayac' not in st.session_state:
    st.session_state.transfer_sayac = 0

with st.sidebar:
    st.markdown("## 🎨 ArtGuard AI")
    st.markdown("---")
    secilen_dil = st.selectbox("🌍 Dil", ["Türkçe", "English"])
    st.markdown("---")
    st.info("💡 Blockchain + AI ile dijital sanat koruması")

sozluk = {
    'Türkçe': {
        'baslik': "🎨 ArtGuard AI - Dijital Sanat Koruma Sistemi",
        'altbaslik': "TÜBİTAK 4006 | Blockchain + Yapay Zeka",
        'istatistik': "📊 Anlık İstatistikler",
        'eser': "Eserler", 'kullanici': "Kullanıcı", 'ai': "AI Uyarı", 'transfer': "Transfer",
        'yukle': "📤 Eser Yükle", 'dosya': "Dosya seç (jpg, png, pdf, mp3...)",
        'hash': "🔐 Hash:", 'tam_hash': "📋 Tam Hash:",
        'kopya': "🚨 KOPYA TESPİT!", 'kopya_msg': "Bu eser kayıtlı!",
        'sahip': "Sahibi:", 'eser_adi': "Eser:",
        'yeni': "✅ Yeni Eser", 'yeni_msg': "Blockchain'e eklenebilir!",
        'ai_uyari': "⚠️ AI: Benzer resim bulundu!",
        'benzerlik': "Benzerlik:", 'calmis': "Çalıntı olabilir!",
        'kayit': "🎨 Kayıt", 'eser_input': "Eser Adı:",
        'sahip_input': "Sahibi:", 'telif': "Telif:",
        'telif_default': "Kopyalama yasak. Tüm haklar saklı.",
        'kaydet': "🔗 KAYDET", 'tamam': "✅ Kaydedildi! Blok #",
        'sertifika': "🎫 Sertifika:", 'indir': "📥 İndir",
        'doldur': "Boş alan bırakma!", 'kayitlar': "📊 Kayıtlar",
        'toplam': "Toplam:", 'blok': "Blok #", 'tarih': "Tarih:",
        'yuzde': "Telif:", 'telif_hakki': "Telif Hakkı:",
        'yok': "Henüz kayıt yok!", 'transfer_baslik': "🔄 Transfer",
        'hangi': "Blok No:", 'yeni_sahip': "Yeni Sahip:",
        'transfer_btn': "Transfer Et", 'transfer_ok': "✅ Tamam! %10 telif:",
        'transfer_msg': "Transfer edildi:", 'yaz': "Sahip adı yaz!",
        'kaydet_yukle': "💾 Kaydet/Yükle", 'json_kaydet': "Kaydet",
        'json_indir': "İndir", 'json_yukle': "Yükle",
        'yuklendi': "✅ Yüklendi!", 'hata': "❌ Hata!",
        'not': "⚠️ Kopyalamayı engellemez, sahipliği kanıtlar. TÜBİTAK 4006."
    },
    'English': {
        'baslik': "🎨 ArtGuard AI - Digital Art Protection",
        'altbaslik': "TÜBİTAK 4006 | Blockchain + AI",
        'istatistik': "📊 Live Stats",
        'eser': "Artworks", 'kullanici': "Users", 'ai': "AI Alerts", 'transfer': "Transfers",
        'yukle': "📤 Upload Art", 'dosya': "Choose file (jpg, png, pdf, mp3...)",
        'hash': "🔐 Hash:", 'tam_hash': "📋 Full Hash:",
        'kopya': "🚨 COPY DETECTED!", 'kopya_msg': "This art is registered!",
        'sahip': "Owner:", 'eser_adi': "Art:",
        'yeni': "✅ New Art", 'yeni_msg': "Can be added to blockchain!",
        'ai_uyari': "⚠️ AI: Similar image found!",
        'benzerlik': "Similarity:", 'calmis': "Maybe stolen!",
        'kayit': "🎨 Register", 'eser_input': "Art Name:",
        'sahip_input': "Owner:", 'telif': "Copyright:",
        'telif_default': "Copying not allowed. All rights reserved.",
        'kaydet': "🔗 SAVE", 'tamam': "✅ Saved! Block #",
        'sertifika': "🎫 Certificate:", 'indir': "📥 Download",
        'doldur': "Fill all fields!", 'kayitlar': "📊 Records",
        'toplam': "Total:", 'blok': "Block #", 'tarih': "Date:",
        'yuzde': "Royalty:", 'telif_hakki': "Copyright:",
        'yok': "No records yet!", 'transfer_baslik': "🔄 Transfer",
        'hangi': "Block No:", 'yeni_sahip': "New Owner:",
        'transfer_btn': "Transfer", 'transfer_ok': "✅ Done! 10% royalty:",
        'transfer_msg': "Transferred:", 'yaz': "Enter owner!",
        'kaydet_yukle': "💾 Save/Load", 'json_kaydet': "Save",
        'json_indir': "Download", 'json_yukle': "Load",
        'yuklendi': "✅ Loaded!", 'hata': "❌ Error!",
        'not': "⚠️ Doesn't stop copying, proves ownership. TÜBİTAK 4006."
    }
}

t = sozluk[secilen_dil]

st.markdown(f"<h1>{t['baslik']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;color:#7f8c8d;font-size:1.1rem;'>{t['altbaslik']}</p>", unsafe_allow_html=True)

st.markdown("---")
st.subheader(t['istatistik'])

k1, k2, k3, k4 = st.columns(4)
kullanici_sayisi = len(set([i['owner'] for i in st.session_state.zincir])) if st.session_state.zincir else 0

with k1:
    st.metric(t['eser'], len(st.session_state.zincir), delta=None, delta_color="off")
with k2:
    st.metric(t['kullanici'], kullanici_sayisi, delta=None, delta_color="off")
with k3:
    st.metric(t['ai'], st.session_state.ai_sayac, delta=None, delta_color="off")
with k4:
    st.metric(t['transfer'], st.session_state.transfer_sayac, delta=None, delta_color="off")

st.markdown("---")

def hash_hesapla(dosya_bytes):
    return hashlib.sha256(dosya_bytes).hexdigest()

def resim_hash_hesapla(resim):
    try:
        return imagehash.average_hash(resim)
    except:
        return None

def benzerlik_kontrol(yeni_hash):
    if yeni_hash is None:
        return None, 0
    en_yuksek = 0
    index = -1
    for i, eski_hash in enumerate(st.session_state.resim_hashler):
        if eski_hash is None:
            continue
        fark = yeni_hash - eski_hash
        benzerlik = 100 * (1 - fark / 64.0)
        if benzerlik > en_yuksek:
            en_yuksek = benzerlik
            index = i
    return index, en_yuksek

def sertifika_yap(blok, dil):
    w, h = 800, 600
    img = Image.new('RGB', (w, h), 'white')
    d = ImageDraw.Draw(img)
    c = (41, 128, 185)
    d.rectangle([10, 10, w-10, h-10], outline=c, width=5)
    d.rectangle([20, 20, w-20, h-20], outline=c, width=2)
    
    qr_veri = f"Block#{blok['index']}|Hash:{blok['file_hash'][:16]}|Owner:{blok['owner']}"
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(qr_veri)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").resize((150, 150))
    img.paste(qr_img, (w - 180, 30))
    
    y = 60
    baslik = "BLOCKCHAIN CERTIFICATE" if dil == 'English' else "BLOCKCHAIN SERTİFİKASI"
    d.text((w//2 - 150, y), baslik, fill=c)
    y += 60
    d.text((50, y), f"{sozluk[dil]['eser_adi']} {blok['art_name']}", fill='black')
    y += 40
    d.text((50, y), f"{sozluk[dil]['sahip']} {blok['owner']}", fill='black')
    y += 40
    d.text((50, y), f"{sozluk[dil]['blok']}{blok['index']}", fill='black')
    y += 40
    d.text((50, y), f"{sozluk[dil]['tarih']}", fill='black')
    y += 25
    d.text((50, y), f"{blok['timestamp'][:19]}", fill='gray')
    y += 40
    d.text((50, y), f"Hash:", fill='black')
    y += 25
    d.text((50, y), f"{blok['file_hash'][:32]}...", fill='gray')
    y += 50
    d.text((50, y), blok['copyright_statement'][:60], fill='darkred')
    alt = "Verified on ArtGuard AI" if dil == 'English' else "ArtGuard AI'de Doğrulandı"
    d.text((w//2 - 120, h - 50), alt, fill='gray')
    return img

st.subheader(t['yukle'])
yuklenen = st.file_uploader(t['dosya'], type=['jpg', 'jpeg', 'png', 'pdf', 'mp3', 'wav', 'txt'])

if yuklenen:
    dosya_bytes = yuklenen.read()
    dosya_hash = hash_hesapla(dosya_bytes)
    kisa = dosya_hash[:16] + "..."
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.code(f"{t['hash']} {kisa}")
    with col_b:
        st.code(f"{t['tam_hash']} {dosya_hash}")
    
    if dosya_hash in st.session_state.hashler:
        st.error(t['kopya'])
        st.warning(t['kopya_msg'])
        for item in st.session_state.zincir:
            if item['file_hash'] == dosya_hash:
                st.info(f"**{t['sahip']}** {item['owner']} | **{t['eser_adi']}** {item['art_name']}")
    else:
        st.success(t['yeni'])
        st.info(t['yeni_msg'])
        
        resim_hash_degeri = None
        
        if yuklenen.type.startswith('image'):
            try:
                resim_dosyasi = Image.open(yuklenen)
                resim_hash_degeri = resim_hash_hesapla(resim_dosyasi)
                
                if len(st.session_state.resim_hashler) > 0:
                    benzer_index, skor = benzerlik_kontrol(resim_hash_degeri)
                    if skor > 80:
                        st.session_state.ai_sayac += 1
                        st.warning(t['ai_uyari'])
                        st.warning(f"**{t['benzerlik']}** {skor:.1f}% ({t['blok']} {benzer_index})")
                        st.warning(t['calmis'])
            except:
                pass
        
        st.markdown("---")
        st.subheader(t['kayit'])
        
        col1, col2 = st.columns(2)
        with col1:
            eser_adi = st.text_input(t['eser_input'])
        with col2:
            sahip_adi = st.text_input(t['sahip_input'])
        
        telif_yazisi = st.text_area(t['telif'], t['telif_default'], height=100)
        
        if st.button(t['kaydet'], use_container_width=True):
            if eser_adi and sahip_adi:
                yeni_blok = {
                    'index': len(st.session_state.zincir),
                    'timestamp': str(datetime.datetime.now()),
                    'art_name': eser_adi,
                    'owner': sahip_adi,
                    'file_hash': dosya_hash,
                    'royalty': 0.1,
                    'copyright_statement': telif_yazisi
                }
                
                st.session_state.zincir.append(yeni_blok)
                st.session_state.hashler.add(dosya_hash)
                st.session_state.resim_hashler.append(resim_hash_degeri)
                
                st.success(f"{t['tamam']}{yeni_blok['index']}")
                st.balloons()
                
                st.info(t['sertifika'])
                sertifika_resmi = sertifika_yap(yeni_blok, secilen_dil)
                
                buffer = BytesIO()
                sertifika_resmi.save(buffer, format='PNG')
                buffer.seek(0)
                
                col_x, col_y = st.columns([1, 3])
                with col_x:
                    st.download_button(t['indir'], buffer, f"cert_{yeni_blok['index']}.png", "image/png", use_container_width=True)
                with col_y:
                    st.image(sertifika_resmi, use_container_width=True)
            else:
                st.error(t['doldur'])

st.markdown("---")
st.header(t['kayitlar'])

if len(st.session_state.zincir) > 0:
    st.write(f"**{t['toplam']}** {len(st.session_state.zincir)}")
    
    for item in st.session_state.zincir:
        with st.expander(f"🎨 {t['blok']}{item['index']} - {item['art_name']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{t['sahip']}** {item['owner']}")
                st.write(f"**{t['tarih']}** {item['timestamp'][:19]}")
            with col2:
                st.write(f"**Hash:** `{item['file_hash'][:20]}...`")
                st.write(f"**{t['yuzde']}** {item['royalty']*100}%")
            st.write(f"**{t['telif_hakki']}** {item['copyright_statement']}")
else:
    st.info(t['yok'])

st.markdown("---")
st.header(t['transfer_baslik'])

if len(st.session_state.zincir) > 0:
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        secilen_blok = st.number_input(t['hangi'], 0, len(st.session_state.zincir)-1, 0)
    with col2:
        yeni_sahip = st.text_input(t['yeni_sahip'])
    with col3:
        st.write("")
        st.write("")
        if st.button(t['transfer_btn'], use_container_width=True):
            if yeni_sahip:
                eski = st.session_state.zincir[secilen_blok]['owner']
                st.session_state.zincir[secilen_blok]['owner'] = yeni_sahip
                st.session_state.transfer_sayac += 1
                st.success(f"{t['transfer_ok']} {eski}")
                st.info(f"{t['transfer_msg']} {yeni_sahip}")
                
                sertifika_resmi = sertifika_yap(st.session_state.zincir[secilen_blok], secilen_dil)
                buffer = BytesIO()
                sertifika_resmi.save(buffer, format='PNG')
                buffer.seek(0)
                st.download_button(t['indir'], buffer, f"transfer_{secilen_blok}.png", "image/png")
            else:
                st.error(t['yaz'])

st.markdown("---")
st.header(t['kaydet_yukle'])

col1, col2 = st.columns(2)

with col1:
    st.subheader("💾 " + t['json_kaydet'])
    if st.button(t['json_kaydet'], use_container_width=True):
        veri = {
            'blockchain': st.session_state.zincir,
            'used_hashes': list(st.session_state.hashler),
            'phash_list': [str(h) if h else None for h in st.session_state.resim_hashler],
            'ai_warnings_count': st.session_state.ai_sayac,
            'transfers_count': st.session_state.transfer_sayac
        }
        json_veri = json.dumps(veri, indent=2, ensure_ascii=False)
        st.download_button(t['json_indir'], json_veri, "blockchain.json", "application/json", use_container_width=True)

with col2:
    st.subheader("📂 " + t['json_yukle'])
    json_dosyasi = st.file_uploader(t['json_yukle'], type=['json'])
    if json_dosyasi:
        try:
            veri = json.load(json_dosyasi)
            st.session_state.zincir = veri['blockchain']
            st.session_state.hashler = set(veri['used_hashes'])
            st.session_state.resim_hashler = [imagehash.hex_to_hash(h) if h else None for h in veri['phash_list']]
            st.session_state.ai_sayac = veri.get('ai_warnings_count', 0)
            st.session_state.transfer_sayac = veri.get('transfers_count', 0)
            st.success(t['yuklendi'])
            st.rerun()
        except:
            st.error(t['hata'])

st.markdown("---")
st.info(t['not'])

st.markdown("<p style='text-align:center;color:#95a5a6;margin-top:2rem;'>Made for TÜBİTAK 4006</p>", unsafe_allow_html=True)
