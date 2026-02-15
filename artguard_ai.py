import streamlit as st
import hashlib
import json
import datetime
from PIL import Image, ImageDraw
import imagehash
import qrcode
from io import BytesIO

# baslangic
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

# dil secimi
secilen_dil = st.sidebar.selectbox("🌍 Dil / Language", ["Türkçe", "English"])

# sozluk
sozluk = {
    'Türkçe': {
        'baslik': "Dijital Sanat Koruma - Blockchain + AI",
        'altbaslik': "TÜBİTAK 4006 Projesi",
        'istatistik_baslik': "📊 İstatistikler",
        'eser_sayisi': "Eserler",
        'kullanici_sayisi': "Kullanıcı",
        'ai_uyari_sayisi': "AI Uyarı",
        'transfer_sayisi': "Transfer",
        'dosya_yukle': "Dosya yükle (jpg, png, pdf, mp3...)",
        'hash_kisa': "Hash:",
        'hash_uzun': "Tam Hash:",
        'kopya_var': "🚨 KOPYA! Bu dosya kayıtlı",
        'kopya_mesaj': "Bu eser blockchain'de var!",
        'kayitli_kisi': "Sahibi:",
        'eser_ismi': "Eser:",
        'yeni_eser_mesaj': "✅ Yeni eser! Ekle",
        'benzer_resim': "⚠️ AI UYARI: Benzer resim bulundu!",
        'benzerlik_orani': "Benzerlik:",
        'calmis_olabilir': "Çalıntı olabilir!",
        'kayit_baslik': "🎨 Blockchain'e Ekle",
        'eser_adi_gir': "Eser Adı:",
        'sahip_adi_gir': "Sahibi:",
        'telif_metni': "Telif Yazısı:",
        'telif_varsayilan': "Kopyalama yasak. Tüm haklar saklı.",
        'kaydet_buton': "🔗 KAYDET",
        'kayit_tamam': "✅ Tamam! Blok #",
        'sertifika_mesaj': "🎫 Sertifika hazır:",
        'sertifika_indir': "📥 İndir",
        'bos_alan_uyari': "Eser adı ve sahip yaz!",
        'kayitlar_baslik': "📊 Kayıtlar",
        'toplam_blok': "Toplam:",
        'blok_no': "Blok #",
        'sahibi': "Sahibi:",
        'tarih_saat': "Tarih:",
        'hash_bilgi': "Hash:",
        'telif_yuzdesi': "Telif:",
        'telif_hakki': "Telif Hakkı:",
        'kayit_yok': "Henüz kayıt yok!",
        'transfer_baslik': "🔄 Transfer",
        'hangi_blok': "Blok No:",
        'yeni_sahip_adi': "Yeni Sahip:",
        'transfer_et_buton': "Transfer Et",
        'transfer_basarili': "✅ Tamam! %10 telif:",
        'transfer_yapildi': "Blok # transfer edildi:",
        'sahip_yaz': "Yeni sahip yaz!",
        'kaydet_yukle_baslik': "💾 Kaydet/Yükle",
        'json_kaydet': "JSON'a Kaydet",
        'json_indir': "İndir",
        'json_yukle': "JSON Yükle",
        'yukleme_basarili': "✅ Yüklendi!",
        'yukleme_hatasi': "Hata!",
        'alt_not': "⚠️ **Not:** Kopyalamayı engellemez ama sahipliği kanıtlar. TÜBİTAK 4006."
    },
    'English': {
        'baslik': "Digital Art Protection - Blockchain + AI",
        'altbaslik': "TÜBİTAK 4006 Project",
        'istatistik_baslik': "📊 Statistics",
        'eser_sayisi': "Artworks",
        'kullanici_sayisi': "Users",
        'ai_uyari_sayisi': "AI Warnings",
        'transfer_sayisi': "Transfers",
        'dosya_yukle': "Upload file (jpg, png, pdf, mp3...)",
        'hash_kisa': "Hash:",
        'hash_uzun': "Full Hash:",
        'kopya_var': "🚨 COPY! File registered",
        'kopya_mesaj': "This art is on blockchain!",
        'kayitli_kisi': "Owner:",
        'eser_ismi': "Art:",
        'yeni_eser_mesaj': "✅ New art! Add it",
        'benzer_resim': "⚠️ AI WARNING: Similar image!",
        'benzerlik_orani': "Similarity:",
        'calmis_olabilir': "Maybe stolen!",
        'kayit_baslik': "🎨 Add to Blockchain",
        'eser_adi_gir': "Art Name:",
        'sahip_adi_gir': "Owner:",
        'telif_metni': "Copyright Text:",
        'telif_varsayilan': "Copying not allowed. All rights reserved.",
        'kaydet_buton': "🔗 SAVE",
        'kayit_tamam': "✅ Done! Block #",
        'sertifika_mesaj': "🎫 Certificate ready:",
        'sertifika_indir': "📥 Download",
        'bos_alan_uyari': "Write art name and owner!",
        'kayitlar_baslik': "📊 Records",
        'toplam_blok': "Total:",
        'blok_no': "Block #",
        'sahibi': "Owner:",
        'tarih_saat': "Date:",
        'hash_bilgi': "Hash:",
        'telif_yuzdesi': "Royalty:",
        'telif_hakki': "Copyright:",
        'kayit_yok': "No records yet!",
        'transfer_baslik': "🔄 Transfer",
        'hangi_blok': "Block No:",
        'yeni_sahip_adi': "New Owner:",
        'transfer_et_buton': "Transfer",
        'transfer_basarili': "✅ Done! 10% royalty:",
        'transfer_yapildi': "Block # transferred:",
        'sahip_yaz': "Write new owner!",
        'kaydet_yukle_baslik': "💾 Save/Load",
        'json_kaydet': "Save JSON",
        'json_indir': "Download",
        'json_yukle': "Load JSON",
        'yukleme_basarili': "✅ Loaded!",
        'yukleme_hatasi': "Error!",
        'alt_not': "⚠️ **Note:** Doesn't stop copying but proves ownership. TÜBİTAK 4006."
    }
}

yazi = sozluk[secilen_dil]

# sayfa
st.title(yazi['baslik'])
st.subheader(yazi['altbaslik'])

# istatistikler
st.markdown("---")
st.subheader(yazi['istatistik_baslik'])

kolon1, kolon2, kolon3, kolon4 = st.columns(4)

kullanici_sayisi = len(set([item['owner'] for item in st.session_state.zincir])) if st.session_state.zincir else 0

with kolon1:
    st.metric(yazi['eser_sayisi'], len(st.session_state.zincir))
with kolon2:
    st.metric(yazi['kullanici_sayisi'], kullanici_sayisi)
with kolon3:
    st.metric(yazi['ai_uyari_sayisi'], st.session_state.ai_sayac)
with kolon4:
    st.metric(yazi['transfer_sayisi'], st.session_state.transfer_sayac)

st.markdown("---")

# hash hesaplama
def hash_hesapla(dosya_bytes):
    return hashlib.sha256(dosya_bytes).hexdigest()

# resim hash
def resim_hash_hesapla(resim):
    try:
        return imagehash.average_hash(resim)
    except:
        return None

# benzerlik kontrolu
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

# sertifika olustur
def sertifika_yap(blok_bilgisi, hangi_dil):
    genislik = 800
    yukseklik = 600
    resim = Image.new('RGB', (genislik, yukseklik), color='white')
    cizim = ImageDraw.Draw(resim)
    
    # cerceve
    renk = (41, 128, 185)
    cizim.rectangle([10, 10, genislik-10, yukseklik-10], outline=renk, width=5)
    cizim.rectangle([20, 20, genislik-20, yukseklik-20], outline=renk, width=2)
    
    # qr kod
    qr_veri = f"Block#{blok_bilgisi['index']}|Hash:{blok_bilgisi['file_hash'][:16]}|Owner:{blok_bilgisi['owner']}"
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(qr_veri)
    qr.make(fit=True)
    qr_resim = qr.make_image(fill_color="black", back_color="white")
    qr_resim = qr_resim.resize((150, 150))
    resim.paste(qr_resim, (genislik - 180, 30))
    
    # yazilar
    y = 60
    
    baslik_txt = "BLOCKCHAIN CERTIFICATE" if hangi_dil == 'English' else "BLOCKCHAIN SERTİFİKASI"
    cizim.text((genislik//2 - 150, y), baslik_txt, fill=renk)
    y += 60
    
    cizim.text((50, y), f"{sozluk[hangi_dil]['eser_ismi']} {blok_bilgisi['art_name']}", fill='black')
    y += 40
    cizim.text((50, y), f"{sozluk[hangi_dil]['sahibi']} {blok_bilgisi['owner']}", fill='black')
    y += 40
    cizim.text((50, y), f"{sozluk[hangi_dil]['blok_no']}{blok_bilgisi['index']}", fill='black')
    y += 40
    cizim.text((50, y), f"{sozluk[hangi_dil]['tarih_saat']}", fill='black')
    y += 25
    cizim.text((50, y), f"{blok_bilgisi['timestamp'][:19]}", fill='gray')
    y += 40
    cizim.text((50, y), f"{sozluk[hangi_dil]['hash_bilgi']}", fill='black')
    y += 25
    cizim.text((50, y), f"{blok_bilgisi['file_hash'][:32]}...", fill='gray')
    y += 50
    cizim.text((50, y), blok_bilgisi['copyright_statement'][:60], fill='darkred')
    
    alt_yazi = "Verified on ArtGuard AI Blockchain" if hangi_dil == 'English' else "ArtGuard AI Blockchain'de Doğrulandı"
    cizim.text((genislik//2 - 120, yukseklik - 50), alt_yazi, fill='gray')
    
    return resim

# dosya yukleme
yuklenen = st.file_uploader(yazi['dosya_yukle'], type=['jpg', 'jpeg', 'png', 'pdf', 'mp3', 'wav', 'txt'])

if yuklenen:
    dosya_bytes = yuklenen.read()
    dosya_hash = hash_hesapla(dosya_bytes)
    kisa_hash = dosya_hash[:16] + "..."
    
    st.write(f"**{yazi['hash_kisa']}** `{kisa_hash}`")
    st.write(f"**{yazi['hash_uzun']}** `{dosya_hash}`")
    
    # kayitli mi kontrol
    if dosya_hash in st.session_state.hashler:
        st.error(yazi['kopya_var'])
        st.warning(yazi['kopya_mesaj'])
        
        for item in st.session_state.zincir:
            if item['file_hash'] == dosya_hash:
                st.info(f"**{yazi['kayitli_kisi']}** {item['owner']} | **{yazi['eser_ismi']}** {item['art_name']}")
    else:
        st.success(yazi['yeni_eser_mesaj'])
        
        # resim kontrolu
        resim_hash_degeri = None
        
        if yuklenen.type.startswith('image'):
            try:
                resim_dosyasi = Image.open(yuklenen)
                resim_hash_degeri = resim_hash_hesapla(resim_dosyasi)
                
                if len(st.session_state.resim_hashler) > 0:
                    benzer_index, skor = benzerlik_kontrol(resim_hash_degeri)
                    if skor > 80:
                        st.session_state.ai_sayac += 1
                        st.warning(yazi['benzer_resim'])
                        st.warning(f"**{yazi['benzerlik_orani']}** {skor:.1f}% ({yazi['blok_no']} {benzer_index})")
                        st.warning(yazi['calmis_olabilir'])
            except:
                pass
        
        # kayit formu
        st.markdown("---")
        st.subheader(yazi['kayit_baslik'])
        
        eser_adi = st.text_input(yazi['eser_adi_gir'], "")
        sahip_adi = st.text_input(yazi['sahip_adi_gir'], "")
        telif_yazisi = st.text_area(yazi['telif_metni'], yazi['telif_varsayilan'])
        
        if st.button(yazi['kaydet_buton']):
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
                
                st.success(f"{yazi['kayit_tamam']}{yeni_blok['index']}")
                st.balloons()
                
                # sertifika
                st.info(yazi['sertifika_mesaj'])
                sertifika_resmi = sertifika_yap(yeni_blok, secilen_dil)
                
                buffer = BytesIO()
                sertifika_resmi.save(buffer, format='PNG')
                buffer.seek(0)
                
                st.download_button(
                    label=yazi['sertifika_indir'],
                    data=buffer,
                    file_name=f"certificate_block_{yeni_blok['index']}.png",
                    mime="image/png"
                )
                
                st.image(sertifika_resmi, caption=f"Certificate - Block #{yeni_blok['index']}", use_container_width=True)
                
            else:
                st.error(yazi['bos_alan_uyari'])

# kayitlari goster
st.markdown("---")
st.header(yazi['kayitlar_baslik'])

if len(st.session_state.zincir) > 0:
    st.write(f"**{yazi['toplam_blok']}** {len(st.session_state.zincir)}")
    
    for item in st.session_state.zincir:
        with st.expander(f"{yazi['blok_no']}{item['index']} - {item['art_name']}"):
            st.write(f"**{yazi['sahibi']}** {item['owner']}")
            st.write(f"**{yazi['tarih_saat']}** {item['timestamp']}")
            st.write(f"**{yazi['hash_bilgi']}** `{item['file_hash'][:20]}...`")
            st.write(f"**{yazi['telif_yuzdesi']}** {item['royalty']*100}%")
            st.write(f"**{yazi['telif_hakki']}** {item['copyright_statement']}")
else:
    st.info(yazi['kayit_yok'])

# transfer
st.markdown("---")
st.header(yazi['transfer_baslik'])

if len(st.session_state.zincir) > 0:
    secilen_blok = st.number_input(yazi['hangi_blok'], min_value=0, 
                                max_value=len(st.session_state.zincir)-1, value=0)
    yeni_sahip = st.text_input(yazi['yeni_sahip_adi'], "")
    
    if st.button(yazi['transfer_et_buton']):
        if yeni_sahip:
            eski_sahip = st.session_state.zincir[secilen_blok]['owner']
            st.session_state.zincir[secilen_blok]['owner'] = yeni_sahip
            st.session_state.transfer_sayac += 1
            st.success(f"{yazi['transfer_basarili']} {eski_sahip}")
            st.info(f"{yazi['transfer_yapildi'].replace('#', f'#{secilen_blok}')} {yeni_sahip}")
            
            # yeni sertifika
            sertifika_resmi = sertifika_yap(st.session_state.zincir[secilen_blok], secilen_dil)
            buffer = BytesIO()
            sertifika_resmi.save(buffer, format='PNG')
            buffer.seek(0)
            
            st.download_button(
                label=yazi['sertifika_indir'],
                data=buffer,
                file_name=f"certificate_transferred_block_{secilen_blok}.png",
                mime="image/png"
            )
        else:
            st.error(yazi['sahip_yaz'])

# kaydet yukle
st.markdown("---")
st.header(yazi['kaydet_yukle_baslik'])

sol, sag = st.columns(2)

with sol:
    if st.button(yazi['json_kaydet']):
        veri = {
            'blockchain': st.session_state.zincir,
            'used_hashes': list(st.session_state.hashler),
            'phash_list': [str(h) if h else None for h in st.session_state.resim_hashler],
            'ai_warnings_count': st.session_state.ai_sayac,
            'transfers_count': st.session_state.transfer_sayac
        }
        
        json_veri = json.dumps(veri, indent=2, ensure_ascii=False)
        st.download_button(yazi['json_indir'], json_veri, "blockchain.json", "application/json")

with sag:
    json_dosyasi = st.file_uploader(yazi['json_yukle'], type=['json'])
    if json_dosyasi:
        try:
            veri = json.load(json_dosyasi)
            st.session_state.zincir = veri['blockchain']
            st.session_state.hashler = set(veri['used_hashes'])
            st.session_state.resim_hashler = [imagehash.hex_to_hash(h) if h else None 
                                           for h in veri['phash_list']]
            st.session_state.ai_sayac = veri.get('ai_warnings_count', 0)
            st.session_state.transfer_sayac = veri.get('transfers_count', 0)
            st.success(yazi['yukleme_basarili'])
            st.rerun()
        except:
            st.error(yazi['yukleme_hatasi'])

# alt not
st.markdown("---")
st.info(yazi['alt_not'])
