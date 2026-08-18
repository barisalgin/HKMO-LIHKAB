import streamlit as st
import pandas as pd
import plotly.express as px
import json
import base64
import os
from core import get_lihkabs, get_jobs_history, get_districts, assign_job, add_lihkab, update_lihkab, toggle_lihkab_status, delete_lihkab, delete_job, clear_all_jobs
from hkmo_pricing import JOB_DEFINITIONS

st.set_page_config(page_title="HKMO Bursa Şube LİHKAB İş Arayüzü", page_icon="logo273x87.png", layout="wide")

def set_background(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(255, 255, 255, 0.94), rgba(255, 255, 255, 0.94)), url(data:image/jpeg;base64,{encoded_string});
                background-size: 50%;
                background-repeat: no-repeat;
                background-position: center center;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

set_background("logo273x87.png")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "permissions" not in st.session_state:
    st.session_state["permissions"] = {}

if not st.session_state["authenticated"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2:
        with st.container(border=True):
            if os.path.exists("logo273x87.png"):
                st.image("logo273x87.png", use_container_width=True)
            st.markdown("<h2 style='text-align: center;'>🔐 LİHKAB Girişi</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>Sisteme erişmek için yetkilendirilmiş bir hesaba ihtiyacınız var.</p>", unsafe_allow_html=True)
            login_user = st.text_input("Kullanıcı Adı")
            login_pass = st.text_input("Şifre", type="password")
            if st.button("Giriş Yap", type="primary", use_container_width=True):
                from core import verify_user
                perms = verify_user(login_user, login_pass)
                if perms is not None:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = login_user
                    if login_user == "barisalgin":
                        st.session_state["permissions"] = {
                            "can_assign_job": True,
                            "can_add_office": True,
                            "can_manage_office": True,
                            "can_fix_errors": True
                        }
                    else:
                        st.session_state["permissions"] = perms
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre hatalı!")
    st.stop()

col_title, col_logout = st.columns([4, 1])
with col_title:
    st.title("Tapu Kadastro Genel Müdürlüğü Bursa İlinde Hizmet Veren LİHKAB İş Takip Listesi")
with col_logout:
    st.write(f"👤 Hoş geldin, **{st.session_state['username']}**")
    if st.button("🚪 Çıkış Yap"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.rerun()

# Sekmeler (Tabs)
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Gösterge Paneli", 
    "➕ Yeni İş Atama", 
    "🏢 Yeni Büro Ekle", 
    "🕒 Atama Geçmişi", 
    "📈 Analitik ve Raporlar",
    "⚙️ Büro Yönetimi",
    "🔐 Yetkilendirme"
])

with tab1:
    st.header("Sistemdeki LİHKAB Büroları ve Kazanç Durumları")
    st.write("Aşağıdaki liste, toplam kazanca göre artan (az kazananlar üstte) şekilde sıralanmıştır.")
    
    lihkabs = get_lihkabs()
    districts = get_districts()
    dist_id_to_name = {d[0]: d[1] for d in districts}
    
    # --- METRICS BÖLÜMÜ ---
    jobs = get_jobs_history()
    toplam_buro = len(lihkabs) if lihkabs else 0
    toplam_is = len(jobs) if jobs else 0
    toplam_hacim = sum(j[4] for j in jobs) if jobs else 0
    toplam_ulasim = sum(j[8] for j in jobs if len(j)>8) if jobs else 0
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Kayıtlı Büro", f"{toplam_buro}")
    col_m2.metric("Dağıtılan İş", f"{toplam_is}")
    col_m3.metric("Toplam İş Hacmi", f"{toplam_hacim:,.2f} ₺")
    col_m4.metric("Toplam Ulaşım Hacmi", f"{toplam_ulasim:,.2f} ₺")
    
    st.write("<br>", unsafe_allow_html=True)
    
    if lihkabs:
        avg_revenue = sum(l[4] for l in lihkabs) / len(lihkabs)
        formatted_lihkabs = []
        for s in lihkabs:
            buro_adi = s[1]
            if s[5] == 0:
                buro_adi += " 🔴 (Pasif)"
                
            active_dist_name = dist_id_to_name.get(s[3], str(s[3]))
                
            trans = s[9] if len(s) > 9 else 0.0
            formatted_lihkabs.append([
                buro_adi, 
                s[2], 
                active_dist_name, 
                avg_revenue,
                s[4],
                trans
            ])
            
        df = pd.DataFrame(formatted_lihkabs, columns=["Büro Adı", "Sahibi", "Bulunduğu İlçe", "Ortalama İş Kazancı (₺)", "Toplam İş Kazancı (₺)", "Toplam Ulaşım Kazancı (₺)"])
        df["Ortalama İş Kazancı (₺)"] = df["Ortalama İş Kazancı (₺)"].apply(lambda x: f"{x:,.2f} ₺")
        df["Toplam İş Kazancı (₺)"] = df["Toplam İş Kazancı (₺)"].apply(lambda x: f"{x:,.2f} ₺")
        df["Toplam Ulaşım Kazancı (₺)"] = df["Toplam Ulaşım Kazancı (₺)"].apply(lambda x: f"{x:,.2f} ₺")
        df.index = df.index + 1
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Sistemde henüz kayıtlı LİHKAB bürosu bulunmamaktadır.")

with tab2:
    st.header("Yeni İş Havuza Ekle")
    if not st.session_state["permissions"].get("can_assign_job", False):
        st.warning("⚠️ Yeni iş atama yetkiniz bulunmamaktadır.", icon="⛔")
    else:
        st.caption("Birim Fiyat Cetveline göre iş bedeli otomatik hesaplanarak dağıtılacaktır.")
    
        if "success_message" in st.session_state:
            st.success(st.session_state["success_message"], icon=":material/check_circle:")
            del st.session_state["success_message"]
    
        districts = get_districts()
    
        with st.container(border=True):
            st.subheader("Konum ve İş Türü", anchor=False)
            col1, col2 = st.columns(2)
            with col1:
                dist_options = {d[1]: d[0] for d in districts} 
                selected_dist_name = st.selectbox("İşin Yapılacağı İlçe", list(dist_options.keys()))
            
            with col2:
                selected_job_name = st.selectbox("İşin Türü", list(JOB_DEFINITIONS.keys()))
        
            col_mahalle, col_ada, col_parsel = st.columns(3)
            with col_mahalle:
                mahalle_adi = st.text_input("Mahalle (Örn: İhsaniye)")
            with col_ada:
                ada_no = st.text_input("Ada No")
            with col_parsel:
                parsel_no = st.text_input("Parsel No")
            
        with st.container(border=True):
            st.subheader(f"{selected_job_name} Bilgileri", anchor=False)
        
            # Dinamik form oluşturma
            job_fields = JOB_DEFINITIONS[selected_job_name]["fields"]
            params = {}
    
        for field_key, field_data in job_fields.items():
            f_type = field_data["type"]
            f_label = field_data["label"]
        
            if f_type == "number":
                default_val = field_data.get("default", 0.0)
                if isinstance(default_val, int):
                    params[field_key] = st.number_input(f_label, min_value=0, value=int(default_val), step=1)
                else:
                    params[field_key] = st.number_input(f_label, min_value=0.0, value=float(default_val), step=0.1)
                
            elif f_type == "select":
                options = field_data.get("options", [])
                params[field_key] = st.selectbox(f_label, options)
            
            elif f_type == "boolean":
                params[field_key] = st.checkbox(f_label, value=field_data.get("default", False))

        st.markdown("<br>", unsafe_allow_html=True)
    
        dist_id = dist_options[selected_dist_name]
        multiplier = next((d[2] for d in districts if d[0] == dist_id), 1.0)
    
        from hkmo_pricing import calculate_price
        current_price = calculate_price(selected_job_name, params, multiplier)
        st.info(f"💡 **Ön İzleme - Hesaplanan HKMO Bedeli:** {current_price:,.2f} ₺")
    
        if st.button("Havuza Gönder ve Dağıt", type="primary"):
            dist_id = dist_options[selected_dist_name]
        
            if mahalle_adi: params["Mahalle"] = mahalle_adi
            if ada_no: params["Ada"] = ada_no
            if parsel_no: params["Parsel"] = parsel_no
        
            assigned_lihkab_id, price, transport_price = assign_job(selected_job_name, dist_id, params, st.session_state["username"])
        
            if assigned_lihkab_id is None:
                 st.error("❌ Sistemde kayıtlı ve aktif hiçbir LİHKAB bulunamadığı için atama yapılamadı!")
            else:
                 assigned_lihkab_name = next((s[1] for s in lihkabs if s[0] == assigned_lihkab_id), "Bilinmeyen Büro")
                 st.session_state["success_message"] = f"✅ İş başarıyla onaylandı ve havuza gönderildi!\n\n🏢 **Atanan Büro:** {assigned_lihkab_name}\n\n💰 **Atanan İşin Bedeli:** {price:,.2f} ₺"
                 st.rerun()

with tab3:
    st.header("Yeni LİHKAB Bürosu Kaydı")
    
    if not st.session_state["permissions"].get("can_add_office", False):
        st.warning("⚠️ Sisteme yeni büro ekleme yetkiniz bulunmamaktadır.", icon="⛔")
    else:
        st.caption("Sisteme yeni bir LİHKAB firması ekleyin.")
        
        if "shkm_success_message" in st.session_state:
            st.success(st.session_state["shkm_success_message"], icon=":material/check_circle:")
            del st.session_state["shkm_success_message"]
            
        with st.container(border=True):
            col_ad, col_sahip = st.columns(2)
            with col_ad:
                new_name = st.text_input("Büro Adı (Örn: Yıldız LİHKAB)")
            with col_sahip:
                new_owner = st.text_input("Sahibi (Mühendis Adı)")
                
            col_sicil, col_uni = st.columns(2)
            with col_sicil:
                new_registry = st.text_input("Oda Sicil No")
            with col_uni:
                new_uni = st.text_input("Mezun Olunan Üniversite")
                
            new_address = st.text_area("Firma Adresi")
            
            dist_names = list(dist_options.keys())
            selected_pref = st.selectbox("Büronun Bulunduğu İlçe (Fiziksel Ofis Konumu)", dist_names)
            
            st.write("<br>", unsafe_allow_html=True)
            if st.button("Büroyu Sisteme Ekle", type="primary"):
                if not new_name or not new_owner:
                    st.error("Lütfen büro adı ve sahibi alanlarını doldurun.", icon=":material/error:")
                else:
                    mevcut_burolar = get_lihkabs()
                    is_duplicate = False
                    for b in mevcut_burolar:
                        if b[1].strip().lower() == new_name.strip().lower() and b[2].strip().lower() == new_owner.strip().lower():
                            is_duplicate = True
                            break
                            
                    if is_duplicate:
                        st.error("⚠️ Bu büro sisteme zaten işli! Aynı isim ve firma sahibiyle birden fazla kayıt yapılamaz.")
                    else:
                        pref_id = dist_options[selected_pref]
                        add_lihkab(new_name, new_owner, pref_id, new_address, new_registry, new_uni)
                        st.session_state["shkm_success_message"] = f"✅ **{new_name}** adlı büro, sahibi **{new_owner}** ile birlikte başarıyla sisteme eklendi!"
                        st.rerun()

with tab4:
    st.header("Geçmiş İş Atamaları")
    jobs = get_jobs_history()
    if jobs:
        formatted_jobs = []
        for j in jobs:
            try:
                params_dict = json.loads(j[6])
                mahalle = params_dict.pop("Mahalle", "")
                ada = params_dict.pop("Ada", "")
                parsel = params_dict.pop("Parsel", "")
                params_str = ", ".join([f"{k}: {v}" for k,v in params_dict.items()])
            except:
                params_str = j[6]
                mahalle = ""
                ada = ""
                parsel = ""
                
            created_by = j[7] if len(j) > 7 else "Sistem"
            transport = j[8] if len(j) > 8 else 0.0
            formatted_jobs.append([j[0], j[1], j[2], j[3], mahalle, ada, parsel, j[4], transport, params_str, j[5], created_by])
            
        if st.session_state["permissions"].get("can_fix_errors", False):
            df_jobs = pd.DataFrame(formatted_jobs, columns=["İş ID", "İş Türü", "İlçe", "Atanan Büro", "Mahalle", "Ada", "Parsel", "Fiyat (₺)", "Ulaşım (₺)", "Detaylar", "Atama Tarihi", "İşlemi Yapan"])
        else:
            formatted_jobs_hidden = [row[:-1] for row in formatted_jobs]
            df_jobs = pd.DataFrame(formatted_jobs_hidden, columns=["İş ID", "İş Türü", "İlçe", "Atanan Büro", "Mahalle", "Ada", "Parsel", "Fiyat (₺)", "Ulaşım (₺)", "Detaylar", "Atama Tarihi"])
        
        # Filtreleme Alanı
        col_filtre1, col_filtre2, col_filtre3 = st.columns(3)
        with col_filtre1:
            buro_listesi = ["Tüm Bürolar"] + sorted(list(df_jobs["Atanan Büro"].unique()))
            secilen_buro = st.selectbox("Büroya Göre Filtrele:", buro_listesi)
            
        with col_filtre2:
            ilce_listesi = ["Tüm İlçeler"] + sorted(list(df_jobs["İlçe"].unique()))
            secilen_ilce = st.selectbox("İlçeye Göre Filtrele:", ilce_listesi)
            
        with col_filtre3:
            tarih_araligi = st.date_input("Tarih Aralığına Göre Filtrele (Başlangıç - Bitiş):", value=())
        
        # Veriyi Filtrele
        df_gosterim = df_jobs.copy()
        
        if secilen_buro != "Tüm Bürolar":
            df_gosterim = df_gosterim[df_gosterim["Atanan Büro"] == secilen_buro]
            
        if secilen_ilce != "Tüm İlçeler":
            df_gosterim = df_gosterim[df_gosterim["İlçe"] == secilen_ilce]
            
        if len(tarih_araligi) == 2:
            baslangic, bitis = tarih_araligi
            df_gosterim["Sadece_Tarih"] = pd.to_datetime(df_gosterim["Atama Tarihi"]).dt.date
            df_gosterim = df_gosterim[(df_gosterim["Sadece_Tarih"] >= baslangic) & (df_gosterim["Sadece_Tarih"] <= bitis)]
            df_gosterim = df_gosterim.drop(columns=["Sadece_Tarih"])
            
        df_ui = df_gosterim.copy()
        df_ui["Fiyat (₺)"] = df_ui["Fiyat (₺)"].apply(lambda x: f"{x:,.2f} ₺")
        st.dataframe(df_ui, use_container_width=True)
        
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_gosterim.to_excel(writer, index=False, sheet_name='Atamalar')
            
        isim_parcalari = []
        if secilen_buro != "Tüm Bürolar": isim_parcalari.append(secilen_buro.replace(' ', '_'))
        if secilen_ilce != "Tüm İlçeler": isim_parcalari.append(secilen_ilce.replace(' ', '_'))
        
        if isim_parcalari:
            dosya_adi = f"LIHKAB_Atama_{'_'.join(isim_parcalari)}.xlsx"
        else:
            dosya_adi = "Tum_LIHKAB_Atamalari.xlsx"
        
        st.download_button(
            label="📥 Excel Olarak İndir",
            data=buffer.getvalue(),
            file_name=dosya_adi,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
        
        if st.session_state["permissions"].get("can_fix_errors", False):
            st.write("<br><hr>", unsafe_allow_html=True)
            st.subheader("🛠️ Admin İşlemleri (İş Kaydı Silme)", anchor=False)
            
            if "job_del_success" in st.session_state:
                st.success(st.session_state["job_del_success"])
                del st.session_state["job_del_success"]
                
            col_del1, col_del2 = st.columns(2)
            with col_del1:
                with st.container(border=True):
                    st.write("**Belirli Bir Atamayı Sil**")
                    job_ids = df_jobs["İş ID"].tolist()
                    selected_job_to_del = st.selectbox("Silinecek İş ID'si:", job_ids)
                    if st.button("🗑️ Seçili İşi Sil"):
                        delete_job(selected_job_to_del)
                        st.session_state["job_del_success"] = f"✅ İş ID {selected_job_to_del} başarıyla silindi ve ilgili büronun kazancı güncellendi."
                        st.rerun()
            
            with col_del2:
                with st.container(border=True):
                    st.write("**Tüm Geçmişi Temizle**")
                    st.error("⚠️ Dikkat: Bu işlem havuzdaki tüm atamaları siler ve LİHKAB kazançlarını sıfırlar.")
                    if st.button("⚠️ Tüm Atamaları Sil"):
                        clear_all_jobs()
                        st.session_state["job_del_success"] = "✅ Tüm geçmiş atamalar silindi ve büro kazançları sıfırlandı."
                        st.rerun()
        
    else:
        st.info("Henüz havuza iş eklenmemiş.")


with tab5:
    st.header("İş Analitiği ve Çapraz Raporlama")
    
    # Tüm iş geçmişini al
    all_jobs_history = get_jobs_history()
    
    if not all_jobs_history:
        st.info("Sistemde analiz edilecek herhangi bir iş geçmişi bulunmamaktadır.")
    else:
        # jobs: (id, job_name, district_name, lihkab_name, price, assigned_at, params_json, created_by, transport_price)
        df_ana = pd.DataFrame(all_jobs_history, columns=[
            "İş ID", "İş Türü", "İşin Çıktığı İlçe", "Atanan Büro", "Fiyat (₺)", 
            "Atama Tarihi", "Detaylar", "İşlemi Yapan", "Ulaşım (₺)"
        ])
        
        # Atanan büroların ilçelerini bulmak için lihkabs tablosunu joinleyelim
        # get_lihkabs() -> id, name, owner, active_district_id, ...
        # district_id_to_name -> dist_id_to_name is already in tab1 but let's re-fetch
        districts = get_districts()
        dist_id_to_name_map = {d[0]: d[1] for d in districts}
        
        lihkabs_list = get_lihkabs()
        # Create a dict mapping bureau name -> its district name
        buro_to_dist_map = {}
        for l in lihkabs_list:
            buro_adi = l[1]
            dist_id = l[3]
            buro_to_dist_map[buro_adi] = dist_id_to_name_map.get(dist_id, "Bilinmiyor")
            
        df_ana["İşi Yapan Büronun İlçesi"] = df_ana["Atanan Büro"].map(buro_to_dist_map)
        
        st.subheader("1. Atama Başarısı ve Taşkın Matrisi (Crosstab)")
        st.write("Bu tablo, hangi ilçeden çıkan işlerin hangi ilçelerdeki bürolar tarafından yapıldığını gösterir. Kendi ilçesine düşmeyen işler **Taşkın** olarak kabul edilir.")
        
        if len(df_ana) > 0:
            crosstab_df = pd.crosstab(df_ana["İşin Çıktığı İlçe"], df_ana["İşi Yapan Büronun İlçesi"])
            
            # Toplam taşkın oranını hesapla
            total_jobs = len(df_ana)
            diagonal_sum = 0
            for col in crosstab_df.columns:
                if col in crosstab_df.index:
                    diagonal_sum += crosstab_df.loc[col, col]
            
            taskin_sayisi = total_jobs - diagonal_sum
            taskin_orani = (taskin_sayisi / total_jobs) * 100 if total_jobs > 0 else 0
            
            col_t1, col_t2 = st.columns(2)
            col_t1.metric("Kendi İlçesinde Kalan İş Oranı", f"%{100 - taskin_orani:.1f}")
            col_t2.metric("Başka İlçeye Taşan İş Oranı (Taşkın)", f"%{taskin_orani:.1f}")
            
            # Isı haritası (Heatmap)
            fig_heatmap = px.imshow(
                crosstab_df, 
                text_auto=True, 
                color_continuous_scale='YlGnBu', 
                labels=dict(x="İşi Yapan Büronun İlçesi", y="İşin Çıktığı İlçe", color="İş Sayısı"),
                aspect="auto"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
        st.write("<hr>", unsafe_allow_html=True)
        
        st.subheader("2. İş Kalemleri Dağılımı")
        col_pie1, col_pie2 = st.columns(2)
        
        with col_pie1:
            # Hangi işten kaç tane var?
            job_counts = df_ana["İş Türü"].value_counts().reset_index()
            job_counts.columns = ["İş Türü", "Adet"]
            fig_pie_jobs = px.pie(job_counts, values="Adet", names="İş Türü", title="İş Türlerine Göre Dağılım", hole=0.3)
            st.plotly_chart(fig_pie_jobs, use_container_width=True)
            
        with col_pie2:
            # Hangi ilçeden ne kadar iş çıkmış?
            dist_counts = df_ana["İşin Çıktığı İlçe"].value_counts().reset_index()
            dist_counts.columns = ["İlçe", "Adet"]
            fig_pie_dist = px.pie(dist_counts, values="Adet", names="İlçe", title="İşlerin Çıktığı İlçelere Göre Dağılım", hole=0.3)
            st.plotly_chart(fig_pie_dist, use_container_width=True)

with tab6:
    st.header("⚙️ Büro Yönetimi (Düzenle / Pasife Al / Sil)")
    
    if not st.session_state["permissions"].get("can_manage_office", False):
        st.warning("⚠️ Büro yönetimi (düzenleme, pasife alma, silme) yetkiniz bulunmamaktadır.", icon="⛔")
    else:
        st.write("Sistemdeki büroların bilgilerini güncelleyebilir, geçici olarak havuzdan çıkarabilir veya kalıcı olarak silebilirsiniz.")
        
        if "mgmt_success" in st.session_state:
            st.success(st.session_state["mgmt_success"])
            del st.session_state["mgmt_success"]
            
        if lihkabs:
            buro_options = {f"{s[1]} ({s[2]})": s for s in lihkabs}
            selected_buro_key = st.selectbox("İşlem Yapılacak Büroyu Seçin:", list(buro_options.keys()))
            selected_buro = buro_options[selected_buro_key]
            
            buro_id = selected_buro[0]
            buro_ad = selected_buro[1]
            buro_sahip = selected_buro[2]
            buro_active_dist = selected_buro[3]
            buro_is_active = selected_buro[5]
            buro_address = selected_buro[6] if len(selected_buro) > 6 and selected_buro[6] else ""
            buro_registry = selected_buro[7] if len(selected_buro) > 7 and selected_buro[7] else ""
            buro_uni = selected_buro[8] if len(selected_buro) > 8 and selected_buro[8] else ""
            
            st.write("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.subheader("Büro Bilgilerini Düzenle", anchor=False)
                
                col_ad, col_sahip = st.columns(2)
                with col_ad:
                    edit_name = st.text_input("Büro Adı", value=buro_ad, key=f"edit_name_{buro_id}")
                with col_sahip:
                    edit_owner = st.text_input("Büro Sahibi", value=buro_sahip, key=f"edit_owner_{buro_id}")
                    
                col_sicil, col_uni = st.columns(2)
                with col_sicil:
                    edit_registry = st.text_input("Oda Sicil No", value=buro_registry, key=f"edit_registry_{buro_id}")
                with col_uni:
                    edit_uni = st.text_input("Mezun Olunan Üniversite", value=buro_uni, key=f"edit_uni_{buro_id}")
                    
                edit_address = st.text_area("Firma Adresi", value=buro_address, key=f"edit_address_{buro_id}")
                
                dist_names = list(dist_options.keys())
                default_dist_index = dist_names.index(dist_id_to_name.get(buro_active_dist)) if dist_id_to_name.get(buro_active_dist) in dist_names else 0
                edit_pref = st.selectbox("Bulunduğu İlçe (Ofis Konumu)", dist_names, index=default_dist_index, key=f"edit_pref_{buro_id}")
            
            if st.button("💾 Değişiklikleri Kaydet", type="primary"):
                if not edit_name or not edit_owner:
                    st.error("Ad ve sahip zorunludur.")
                else:
                    new_pref_id = dist_options[edit_pref]
                    update_lihkab(buro_id, edit_name, edit_owner, new_pref_id, edit_address, edit_registry, edit_uni)
                    st.session_state["mgmt_success"] = f"✅ {edit_name} bilgileri güncellendi."
                    st.rerun()
                    
            st.write("<br>", unsafe_allow_html=True)
            col_status, col_delete = st.columns(2)
            
            with col_status:
                with st.container(border=True):
                    st.subheader("Durum Değiştir", anchor=False)
                if buro_is_active == 1:
                    st.info("Bu büro şu an **AKTİF**. Havuzdan iş alabilir.")
                    if st.button("⏸️ Büroyu Pasife Al"):
                        toggle_lihkab_status(buro_id, 1)
                        st.session_state["mgmt_success"] = f"⏸️ {buro_ad} pasife alındı. Havuzdan iş almayacak."
                        st.rerun()
                else:
                    st.warning("Bu büro şu an **PASİF**. Havuzdan iş almıyor.")
                    if st.button("▶️ Büroyu Aktifleştir"):
                        toggle_lihkab_status(buro_id, 0)
                        st.session_state["mgmt_success"] = f"▶️ {buro_ad} aktifleştirildi. Tekrar havuza dahil edildi."
                        st.rerun()
                        
            with col_delete:
                with st.container(border=True):
                    st.subheader("Büroyu Sil", anchor=False)
                st.error("Dikkat: Büroyu sildiğinizde havuzdan tamamen çıkarılır.")
                if st.button("🗑️ Kalıcı Olarak Sil"):
                    delete_lihkab(buro_id)
                    st.session_state["mgmt_success"] = f"🗑️ {buro_ad} sistemden tamamen silindi."
                    st.rerun()
        else:
            st.info("Sistemde işlem yapılacak büro bulunmamaktadır.")

with tab7:
    st.header("🔐 Yetkilendirme (Kullanıcı Yönetimi)")
    from core import get_users, add_user_db, delete_user_db, change_password_db, update_user_permissions_db
    
    if "admin_msg" in st.session_state:
        st.success(st.session_state["admin_msg"])
        del st.session_state["admin_msg"]

    if st.session_state["username"] != "barisalgin":
        st.warning("⚠️ Yeni kullanıcı ekleme, silme ve yetki düzenleme yetkisi sadece sistem kurucusuna (barisalgin) aittir.", icon="⛔")
        st.write("Ancak kendi şifrenizi aşağıdan değiştirebilirsiniz:")
        
        users = get_users()
        current_u_id = next((u[0] for u in users if u[1] == st.session_state["username"]), None)
        
        with st.container(border=True):
            st.subheader("🔑 Şifremi Değiştir", anchor=False)
            new_pass = st.text_input("Yeni Şifreniz", type="password", key="self_edit_p")
            if st.button("💾 Şifremi Güncelle"):
                if new_pass and current_u_id:
                    change_password_db(current_u_id, new_pass)
                    st.session_state["admin_msg"] = "Şifreniz başarıyla güncellendi!"
                    st.rerun()
                else:
                    st.error("Lütfen yeni şifrenizi girin.")
    else:
        st.write("Sisteme giriş yapabilecek kişileri ve yetkilerini buradan yönetebilirsiniz.")
        
        users = get_users()
        
        col_new_user, col_edit_user = st.columns(2)
        with col_new_user:
            with st.container(border=True):
                st.subheader("Yeni Kullanıcı Ekle", anchor=False)
                new_u = st.text_input("Kullanıcı Adı", key="new_u")
                new_p = st.text_input("Şifre", type="password", key="new_p")
                
                st.write("**Yetkiler**")
                can_assign = st.checkbox("Yeni İş Atayabilir", key="new_can_assign")
                can_add = st.checkbox("Yeni Büro Ekleyebilir", key="new_can_add")
                can_manage = st.checkbox("Büro Yönetebilir (Düzenle/Pasife Al/Sil)", key="new_can_manage")
                can_fix = st.checkbox("Hatalı Atamaları Silebilir", key="new_can_fix")
                
                if st.button("➕ Kullanıcıyı Ekle", type="primary"):
                    if new_u and new_p:
                        if add_user_db(new_u, new_p, can_assign, can_add, can_manage, can_fix):
                            st.session_state["admin_msg"] = f"Kullanıcı '{new_u}' başarıyla eklendi."
                            st.rerun()
                        else:
                            st.error("Bu kullanıcı adı zaten mevcut!")
                    else:
                        st.error("Lütfen tüm alanları doldurun.")
                        
        with col_edit_user:
            with st.container(border=True):
                st.subheader("Mevcut Kullanıcıları Yönet", anchor=False)
                user_options = {u[1]: u for u in users}
                if user_options:
                    selected_u = st.selectbox("İşlem Yapılacak Kullanıcı:", list(user_options.keys()))
                    u_data = user_options[selected_u]
                    u_id = u_data[0]
                    u_can_assign = bool(u_data[3])
                    u_can_add = bool(u_data[4])
                    u_can_manage = bool(u_data[5])
                    u_can_fix = bool(u_data[6])
                    
                    st.write("**Kullanıcı Yetkilerini Düzenle**")
                    edit_can_assign = st.checkbox("Yeni İş Atayabilir", value=u_can_assign, key=f"edit_can_assign_{u_id}")
                    edit_can_add = st.checkbox("Yeni Büro Ekleyebilir", value=u_can_add, key=f"edit_can_add_{u_id}")
                    edit_can_manage = st.checkbox("Büro Yönetebilir", value=u_can_manage, key=f"edit_can_manage_{u_id}")
                    edit_can_fix = st.checkbox("Hatalı Atamaları Silebilir", value=u_can_fix, key=f"edit_can_fix_{u_id}")
                    
                    if st.button("💾 Yetkileri Kaydet"):
                        update_user_permissions_db(u_id, edit_can_assign, edit_can_add, edit_can_manage, edit_can_fix)
                        st.session_state["admin_msg"] = f"'{selected_u}' adlı kullanıcının yetkileri güncellendi."
                        st.rerun()

                    st.write("<hr>", unsafe_allow_html=True)
                    new_pass = st.text_input("Yeni Şifre Belirle", type="password", key=f"edit_p_{u_id}")
                    if st.button("🔑 Şifreyi Güncelle"):
                        if new_pass:
                            change_password_db(u_id, new_pass)
                            st.session_state["admin_msg"] = f"'{selected_u}' adlı kullanıcının şifresi güncellendi."
                            st.rerun()
                        else:
                            st.error("Lütfen yeni şifre girin.")
                    
                    st.write("<br>", unsafe_allow_html=True)
                    if st.button("🗑️ Kullanıcıyı Sistemden Sil"):
                        if selected_u == st.session_state["username"]:
                            st.error("Şu anda aktif olduğunuz hesabı silemezsiniz!")
                        elif selected_u == "barisalgin":
                            st.error("Sistem yöneticisini silemezsiniz!")
                        else:
                            delete_user_db(u_id)
                            st.session_state["admin_msg"] = f"'{selected_u}' kalıcı olarak silindi."
                            st.rerun()
                else:
                    st.info("Kayıtlı kullanıcı bulunamadı.")
