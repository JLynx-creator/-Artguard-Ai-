import streamlit as st
import hashlib
import json
import datetime
from PIL import Image, ImageDraw
import imagehash
import qrcode
from io import BytesIO

st.set_page_config(page_title="ArtGuard AI", page_icon="🎨", layout="wide")

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
    tema = st.selectbox("🎨 Tema", ["Mor-Mavi", "Turuncu-Kırmızı", "Yeşil-Mavi", "Pembe-Mor", "Koyu Mod", "Altın-Sarı", "Gümüş-Şehir", "Deniz-Mavin", "Gün Batımı", "Orman-Yeşil", "Lacivert-Gümüş", "Mercan-Turkuaz", "Eflatun-Gri", "Ateş-Kırmızı", "Buz-Mavi"])
    st.markdown("---")
    st.info("💡 Blockchain + AI")

temalar = {
    "Mor-Mavi": {'g1': '#667eea', 'g2': '#764ba2'},
    "Turuncu-Kırmızı": {'g1': '#f46b45', 'g2': '#eea849'},
    "Yeşil-Mavi": {'g1': '#11998e', 'g2': '#38ef7d'},
    "Pembe-Mor": {'g1': '#ee0979', 'g2': '#ff6a00'},
    "Koyu Mod": {'g1': '#2c3e50', 'g2': '#34495e'},
    "Altın-Sarı": {'g1': '#f7971e', 'g2': '#ffd200'},
    "Gümüş-Şehir": {'g1': '#bdc3c7', 'g2': '#2c3e50'},
    "Deniz-Mavin": {'g1': '#2193b0', 'g2': '#6dd5ed'},
    "Gün Batımı": {'g1': '#ff6b6b', 'g2': '#feca57'},
    "Orman-Yeşil": {'g1': '#134e5e', 'g2': '#71b280'},
    "Lacivert-Gümüş": {'g1': '#4b6cb7', 'g2': '#182848'},
    "Mercan-Turkuaz": {'g1': '#ff6b9d', 'g2': '#c44569'},
    "Eflatun-Gri": {'g1': '#8e44ad', 'g2': '#95a5a6'},
    "Ateş-Kırmızı": {'g1': '#ff416c', 'g2': '#ff4b2b'},
    "Buz-Mavi": {'g1': '#4facfe', 'g2': '#00f2fe'}
}

t_renk = temalar[tema]

st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, {t_renk['g1']} 50%, {t_renk['g2']} 50%);
    }}
    .main .block-container {{
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }}
    h1 {{
        color: #2c3e50;
        text-align: center;
    }}
    h2 {{
        color: #34495e;
        border-bottom: 2px solid {t_renk['g1']};
    }}
    .stButton > button {{
        background: linear-gradient(90deg, {t_renk['g1']}, {t_renk['g2']});
        color: white;
        border-radius: 20px;
        padding: 0.6rem 2rem;
        border: none;
    }}
</style>
""", unsafe_allow_html=True)

sozluk = {
    'Türkçe': {
        'baslik': "🎨 ArtGuard AI - Dijital Sanat Koruma",
        'altbaslik': "TÜBİTAK 4006 Projesi",
        'istatistik': "📊 İstatistikler",
        'eser': "Eserler", 'kullanici': "Kullanıcı", 'ai': "AI Uyarı", 'transfer': "Transfer",
        'yukle': "📤 Dosya Yükle", 'dosya': "Dosya seç",
        'hash': "Hash:", 'tam_hash': "Tam Hash:",
        'kopya': "🚨 KOPYA!", 'kopya_msg': "Bu eser kayıtlı!",
        'sahip': "Sahibi:", 'eser_adi': "Eser:",
        'yeni': "✅ Yeni Eser", 'yeni_msg': "Blockchain'e eklenebilir",
        'ai_uyari': "⚠️ Benzer resim bulundu!",
        'benzerlik': "Benzerlik:", 'calmis': "Çalıntı olabilir!",
        'kayit': "🎨 Kayıt", 'eser_input': "Eser Adı:",
        'sahip_input': "Sahibi:", 'telif': "Telif:",
        'telif_default': "Kopyalama yasak. Tüm haklar saklı.",
        'kaydet': "KAYDET", 'tamam': "✅ Kaydedildi! Blok #",
        'sertifika': "🎫 Sertifika:", 'indir': "İndir",
        'doldur': "Boş alan bırakma!", 'kayitlar': "📊 Kayıtlar",
        'toplam': "Toplam:", 'blok': "Blok #", 'tarih': "Tarih:",
        'yuzde': "Telif:", 'telif_hakki': "Telif Hakkı:",
        'yok': "Henüz kayıt yok!", 'transfer_baslik': "🔄 Transfer",
        'hangi': "Blok No:", 'yeni_sahip': "Yeni Sahip:",
        'transfer_btn': "Transfer Et", 'transfer_ok': "✅ Tamam! %10 telif:",
        'transfer_msg': "Transfer edildi", 'yaz': "Sahip adı yaz!",
        'kaydet_yukle': "💾 Kaydet/Yükle", 'json_kaydet': "Kaydet",
        'json_indir': "İndir", 'json_yukle': "Yükle",
        'yuklendi': "✅ Yüklendi!", 'hata': "Hata!",
        'not': "Kopyalamayı engellemez, sahipliği kanıtlar."
    },
    'English': {
        'baslik': "🎨 ArtGuard AI - Digital Art Protection",
        'altbaslik': "TÜBİTAK 4006 Project",
        'istatistik': "📊 Statistics",
        'eser': "Artworks", 'kullanici': "Users", 'ai': "AI Alerts", 'transfer': "Transfers",
        'yukle': "📤 Upload", 'dosya': "Choose file",
        'hash': "Hash:", 'tam_hash': "Full Hash:",
        'kopya': "🚨 COPY!", 'kopya_msg': "This art is registered!",
        'sahip': "Owner:", 'eser_adi': "Art:",
        'yeni': "✅ New Art", 'yeni_msg': "Can be added",
        'ai_uyari': "⚠️ Similar image!",
        'benzerlik': "Similarity:", 'calmis': "Maybe stolen!",
        'kayit': "🎨 Register", 'eser_input': "Art Name:",
        'sahip_input': "Owner:", 'telif': "Copyright:",
        'telif_default': "Copying not allowed. All rights reserved.",
        'kaydet': "SAVE", 'tamam': "✅ Saved! Block #",
        'sertifika': "🎫 Certificate:", 'indir': "Download",
        'doldur': "Fill all fields!", 'kayitlar': "📊 Records",
        'toplam': "Total:", 'blok': "Block #", 'tarih': "Date:",
        'yuzde': "Royalty:", 'telif_hakki': "Copyright:",
        'yok': "No records yet!", 'transfer_baslik': "🔄 Transfer",
        'hangi': "Block No:", 'yeni_sahip': "New Owner:",
        'transfer_btn': "Transfer", 'transfer_ok': "✅ Done! 10% royalty:",
        'transfer_msg': "Transferred", 'yaz': "Enter owner!",
        'kaydet_yukle': "💾 Save/Load", 'json_kaydet': "Save",
        'json_indir': "Download", 'json_yukle': "Load",
        'yuklendi': "✅ Loaded!", 'hata': "Error!",
        'not': "Doesn't stop copying, proves ownership."
    }
}

t = sozluk[secilen_dil]

st.title(t['baslik'])
st.caption(t['altbaslik'])
st.markdown("---")

st.subheader(t['istatistik'])
k1, k2, k3, k4 = st.columns(4)
kullanici_sayisi = len(set([i['owner'] for i in st.session_state.zincir])) if st.session_state.zincir else 0

with k1:
    st.metric(t['eser'], len(st.session_state.zincir))
with k2:
    st.metric(t['kullanici'], kullanici_sayisi)
with k3:
    st.metric(t['ai'], st.session_state.ai_sayac)
with k4:
    st.metric(t['transfer'], st.session_state.transfer_sayac)

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
    
    sahip_temiz = blok['owner'].replace('ş','s').replace('Ş','S').replace('ğ','g').replace('Ğ','G').replace('ü','u').replace('Ü','U').replace('ö','o').replace('Ö','O').replace('ç','c').replace('Ç','C').replace('ı','i').replace('İ','I')
    qr_veri = f"Block:{blok['index']}|Hash:{blok['file_hash'][:16]}|Owner:{sahip_temiz}"
    
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(qr_veri)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").resize((150, 150))
    img.paste(qr_img, (w - 180, 30))
    
    y = 60
    baslik = "BLOCKCHAIN CERTIFICATE" if dil == 'English' else "BLOCKCHAIN SERTIFIKASI"
    d.text((w//2 - 150, y), baslik, fill=c)
    y += 60
    d.text((50, y), f"{sozluk[dil]['eser_adi']} {blok['art_name']}", fill='black')
    y += 40
    d.text((50, y), f"{sozluk[dil]['sahip']} {blok['owner']}", fill='black')
    y += 40
    d.text((50, y), f"{sozluk[dil]['blok']}{blok['index']}", fill='black')
    y += 40
    d.text((50, y), f"{blok['timestamp'][:19]}", fill='gray')
    y += 40
    d.text((50, y), f"Hash: {blok['file_hash'][:32]}...", fill='gray')
    y += 40
    d.text((50, y), blok['copyright_statement'][:60], fill='darkred')
    alt = "ArtGuard AI Blockchain"
    d.text((w//2 - 100, h - 50), alt, fill='gray')
    return img

st.subheader(t['yukle'])
yuklenen = st.file_uploader(t['dosya'], type=['jpg', 'jpeg', 'png', 'pdf', 'mp3', 'wav', 'txt'])

if yuklenen:
    dosya_bytes = yuklenen.read()
    dosya_hash = hash_hesapla(dosya_bytes)
    kisa = dosya_hash[:16] + "..."
    
    st.write(f"**{t['hash']}** `{kisa}`")
    
    if dosya_hash in st.session_state.hashler:
        st.error(t['kopya'])
        st.warning(t['kopya_msg'])
        for item in st.session_state.zincir:
            if item['file_hash'] == dosya_hash:
                st.info(f"**{t['sahip']}** {item['owner']} | **{t['eser_adi']}** {item['art_name']}")
    else:
        st.success(t['yeni'])
        
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
            except:
                pass
        
        st.markdown("---")
        st.subheader(t['kayit'])
        
        col1, col2 = st.columns(2)
        with col1:
            eser_adi = st.text_input(t['eser_input'])
        with col2:
            sahip_adi = st.text_input(t['sahip_input'])
        
        telif_yazisi = st.text_area(t['telif'], t['telif_default'], height=80)
        
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
                
                sertifika_resmi = sertifika_yap(yeni_blok, secilen_dil)
                buffer = BytesIO()
                sertifika_resmi.save(buffer, format='PNG')
                buffer.seek(0)
                
                st.download_button(t['indir'], buffer, f"cert_{yeni_blok['index']}.png", "image/png")
                st.image(sertifika_resmi, use_container_width=True)
            else:
                st.error(t['doldur'])

st.markdown("---")
st.header(t['kayitlar'])

if len(st.session_state.zincir) > 0:
    st.write(f"**{t['toplam']}** {len(st.session_state.zincir)}")
    
    for item in st.session_state.zincir:
        with st.expander(f"{t['blok']}{item['index']} - {item['art_name']}"):
            st.write(f"**{t['sahip']}** {item['owner']}")
            st.write(f"**{t['tarih']}** {item['timestamp'][:19]}")
            st.write(f"**Hash:** `{item['file_hash'][:20]}...`")
            st.write(f"**{t['yuzde']}** {item['royalty']*100}%")
            st.write(f"**{t['telif_hakki']}** {item['copyright_statement']}")
else:
    st.info(t['yok'])

st.markdown("---")
st.header(t['transfer_baslik'])

if len(st.session_state.zincir) > 0:
    col1, col2 = st.columns([2, 2])
    with col1:
        secilen_blok = st.number_input(t['hangi'], 0, len(st.session_state.zincir)-1, 0)
    with col2:
        yeni_sahip = st.text_input(t['yeni_sahip'])
    
    if st.button(t['transfer_btn']):
        if yeni_sahip:
            eski = st.session_state.zincir[secilen_blok]['owner']
            st.session_state.zincir[secilen_blok]['owner'] = yeni_sahip
            st.session_state.transfer_sayac += 1
            st.success(f"{t['transfer_ok']} {eski}")
            
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
    if st.button(t['json_kaydet']):
        veri = {
            'blockchain': st.session_state.zincir,
            'used_hashes': list(st.session_state.hashler),
            'phash_list': [str(h) if h else None for h in st.session_state.resim_hashler],
            'ai_warnings_count': st.session_state.ai_sayac,
            'transfers_count': st.session_state.transfer_sayac
        }
        json_veri = json.dumps(veri, indent=2, ensure_ascii=False)
        st.download_button(t['json_indir'], json_veri, "blockchain.json", "application/json")

with col2:
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
