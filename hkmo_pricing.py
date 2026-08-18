# LİHKAB Hizmet Ücretleri Fiyatlandırma Motoru

JOB_DEFINITIONS = {
    "Aplikasyon": {
        "fields": {
            "alan": {"type": "number", "label": "Toplam Alan (m²)", "default": 1000},
            "kadastro_parseli": {"type": "boolean", "label": "Kadastro parseli mi? (Bedelin 2/3'ü tahsil edilir)", "default": False},
            "kroki_talebi": {"type": "boolean", "label": "Aynı yere ait 1 aplikasyon krokisi ilave talebi", "default": False},
            "bina_sayisi": {"type": "number", "label": "Röperli Kroki için Parsel Üzerindeki Bina Sayısı", "default": 0}
        }
    },
    "Kadastral Yol Sınırlarının Belirlenmesi": {
        "fields": {
            "nokta_sayisi": {"type": "number", "label": "Nokta Sayısı", "default": 1}
        }
    },
    "Cins Değişikliği (Yapısız İken Yapılı, 1 Bina)": {
        "fields": {
            "taban_alani": {"type": "number", "label": "İnşaat Taban Alanı (m²)", "default": 100},
            "ilave_bina_sayisi": {"type": "number", "label": "İlave Bina Sayısı", "default": 0}
        }
    },
    "Cins Değişikliği (Kat İlavesi)": {
        "fields": {}
    },
    "Cins Değişikliği (GES vb.)": {
        "fields": {
            "taban_alani": {"type": "number", "label": "Tesis Taban Alanı (m²)", "default": 100},
            "ilave_bina_sayisi": {"type": "number", "label": "İlave Bina Sayısı", "default": 0}
        }
    },
    "Cins Değişikliği (Yapılı İken Yapısız)": {
        "fields": {}
    },
    "Cins Değişikliği (Bağ, Bahçe, Arsa vs.)": {
        "fields": {
            "araziye_gidilecek_mi": {"type": "boolean", "label": "Araziye gidilmesi gerekli mi?", "default": False}
        }
    },
    "Cins Değişikliği (Sera vb. Tarımsal)": {
        "fields": {}
    },
    "Birleştirme": {
        "fields": {
            "parsel_sayisi": {"type": "number", "label": "Parsel Sayısı (En az 2)", "default": 2}
        }
    },
    "Arzi İrtifak Hakkı": {
        "fields": {
            "parsel_sayisi": {"type": "number", "label": "Parsel Sayısı (En az 2)", "default": 2}
        }
    },
    "Parselin Yerinde Gösterilmesi": {
        "fields": {
            "parsel_sayisi": {"type": "number", "label": "Parsel Sayısı", "default": 1},
            "ayni_malik_ilave": {"type": "number", "label": "Aynı malike ait birbirine bitişik ilave parsel sayısı", "default": 0}
        }
    },
    "Bağımsız Bölümün Yerinde Tespiti": {
        "fields": {
            "bolum_sayisi": {"type": "number", "label": "Bağımsız Bölüm Sayısı", "default": 1},
            "ayni_malik_ilave": {"type": "number", "label": "Aynı malike ait aynı parselde ilave bölüm sayısı", "default": 0}
        }
    },
    "Hatalı Bağımsız Bölüm Düzeltme Teknik Rapor": {
        "fields": {
            "bolum_sayisi": {"type": "number", "label": "Düzeltmeye Konu Bağımsız Bölüm Sayısı (En az 2)", "default": 2}
        }
    },
    "İmar Barışı Zemin Tespit Tutanağı": {
        "fields": {
            "taban_alani": {"type": "number", "label": "Bina İnşaat Taban Alanı (m²)", "default": 100}
        }
    },
    "Plan Örneği": {
        "fields": {
            "parsel_sayisi": {"type": "number", "label": "Parsel Sayısı", "default": 1}
        }
    }
}

def calculate_price(job_name, params, multiplier=1.0):
    price = 0.0
    
    # Yardımcı Fonksiyon: Maktu bedeller katsayı (multiplier) uygulanmadan hesaplanır.
    # Normal bedeller katsayı ile çarpılır.
    
    if job_name == "Aplikasyon":
        alan = params.get("alan", 0)
        base_price = 0.0
        
        if alan <= 1000:
            base_price = 7471
        elif alan <= 3000:
            base_price = 11181
        elif alan <= 5000:
            base_price = 15930
        elif alan <= 10000:
            base_price = 19346
        elif alan <= 20000:
            base_price = 21026
        elif alan <= 50000:
            base_price = 24095
        elif alan <= 100000:
            base_price = 28817
        elif alan <= 200000:
            base_price = 35621
        elif alan <= 500000:
            base_price = 57661
        else:
            base_price = 57661
            extra_area = alan - 500000
            extra_chunks = int(extra_area / 100000)
            if extra_area % 100000 > 0:
                extra_chunks += 1
            base_price += extra_chunks * 10167
            
        # Kadastro Parseli ise 2/3'ü tahsil edilir
        if params.get("kadastro_parseli", False):
            base_price = base_price * (2.0 / 3.0)
            
        # Ana aplikasyon fiyatı katsayıdan etkilenir
        price += base_price * multiplier
        
        # Maktu Ekler (Katsayıdan etkilenmez)
        if params.get("kroki_talebi", False):
            price += 347
            
        bina_sayisi = params.get("bina_sayisi", 0)
        if bina_sayisi > 0:
            # Not 8'e göre röperli kroki maktu 3579 TL
            price += bina_sayisi * 3579

    elif job_name == "Kadastral Yol Sınırlarının Belirlenmesi":
        nokta_sayisi = params.get("nokta_sayisi", 1)
        
        # Bu kalemler "(Maktu*)" olarak işaretlenmiş, yani katsayı uygulanmayacak.
        base_price = 7471
        if nokta_sayisi > 10:
            base_price += (nokta_sayisi - 10) * 320
        price += base_price

    elif job_name == "Cins Değişikliği (Yapısız İken Yapılı, 1 Bina)" or job_name == "Cins Değişikliği (GES vb.)":
        taban = params.get("taban_alani", 0)
        ilave = params.get("ilave_bina_sayisi", 0)
        
        base_price = 7738
        if taban > 500:
            base_price += (taban - 500) * 1.07
            
        price += base_price * multiplier
        price += ilave * 2722 # Maktu ilave

    elif job_name == "Cins Değişikliği (Kat İlavesi)":
        price += 2722 # Maktu

    elif job_name == "Cins Değişikliği (Yapılı İken Yapısız)":
        price += 5100 # Maktu

    elif job_name == "Cins Değişikliği (Bağ, Bahçe, Arsa vs.)":
        price += 2722 # Maktu
        if params.get("araziye_gidilecek_mi", False):
            price += 2375 # Maktu ilave
            
    elif job_name == "Cins Değişikliği (Sera vb. Tarımsal)":
        price += 17169 # Maktu

    elif job_name == "Birleştirme":
        parsel_sayisi = params.get("parsel_sayisi", 2)
        if parsel_sayisi < 2: parsel_sayisi = 2
        
        base_price = 8806
        ilave_parsel = parsel_sayisi - 2
        if ilave_parsel > 0:
            # İlave her bir parsel için %10 artış uygulanır
            base_price = 8806 * (1 + (ilave_parsel * 0.10))
            
        price += base_price * multiplier

    elif job_name == "Arzi İrtifak Hakkı":
        parsel_sayisi = params.get("parsel_sayisi", 2)
        if parsel_sayisi < 2: parsel_sayisi = 2
        
        price += 5096 * multiplier
        ilave = parsel_sayisi - 2
        if ilave > 0:
            price += ilave * 2722 # Maktu

    elif job_name == "Parselin Yerinde Gösterilmesi":
        parsel_sayisi = params.get("parsel_sayisi", 1)
        ayni_malik = params.get("ayni_malik_ilave", 0)
        
        # Ana maktu bedel
        price += parsel_sayisi * 2375
        # Aynı malike ait maktu ilave
        price += ayni_malik * 508

    elif job_name == "Bağımsız Bölümün Yerinde Tespiti":
        bolum_sayisi = params.get("bolum_sayisi", 1)
        ayni_malik = params.get("ayni_malik_ilave", 0)
        
        price += bolum_sayisi * 2375
        price += ayni_malik * 508

    elif job_name == "Hatalı Bağımsız Bölüm Düzeltme Teknik Rapor":
        bolum_sayisi = params.get("bolum_sayisi", 2)
        if bolum_sayisi < 2: bolum_sayisi = 2
        
        price += 3630 # Maktu
        ilave = bolum_sayisi - 2
        if ilave > 0:
            price += ilave * 460 # Maktu

    elif job_name == "İmar Barışı Zemin Tespit Tutanağı":
        taban = params.get("taban_alani", 0)
        base_price = 7817
        if taban > 100:
            base_price += (taban - 100) * 15.63
            
        # PDF Not: "İl katsayısı uygulanmayacaktır"
        price += base_price

    elif job_name == "Plan Örneği":
        parsel_sayisi = params.get("parsel_sayisi", 1)
        price += parsel_sayisi * 540 # Maktu

    if price < 4315 and job_name == "Aplikasyon":
        price = 4315
        
    return round(price, 2)
