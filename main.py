class SHKM:
    def __init__(self, isim, sahip, il, ilce):
        self.isim = isim
        self.sahip = sahip
        self.il = il
        self.ilce = ilce
        self.isler = []

    def is_ata(self, harita_isi):
        self.isler.append(harita_isi)
        print(f"[{self.isim}] bürosuna yeni iş atandı: {harita_isi.is_adi}")

    def __str__(self):
        return f"{self.isim} (Sahibi: {self.sahip}, Konum: {self.il}/{self.ilce})"


class HaritaIsi:
    def __init__(self, is_adi, is_turu, ada, parsel):
        self.is_adi = is_adi
        self.is_turu = is_turu
        self.ada = ada
        self.parsel = parsel
        self.durum = "Bekliyor"

    def durumu_guncelle(self, yeni_durum):
        self.durum = yeni_durum

    def __str__(self):
        return f"İş: {self.is_adi} | Tür: {self.is_turu} | Konum: Ada {self.ada}, Parsel {self.parsel} | Durum: {self.durum}"


def main():
    # 3-4 tane örnek Harita Kadastro Mühendislik Bürosu (SHKM) tanımlıyoruz.
    buro1 = SHKM("Kuzey Harita", "Ahmet Yılmaz", "İstanbul", "Kadıköy")
    buro2 = SHKM("Güney Harita", "Ayşe Demir", "Antalya", "Muratpaşa")
    buro3 = SHKM("Merkez Harita", "Mehmet Kaya", "Ankara", "Çankaya")
    buro4 = SHKM("Doğu Harita", "Ali Can", "Erzurum", "Yakutiye")

    buro_listesi = [buro1, buro2, buro3, buro4]

    print("--- Kayıtlı SHKM Büroları ---")
    for buro in buro_listesi:
        print(buro)
    
    print("\n--- Örnek İş Atamaları ---")
    
    # Örnek işler (HaritaIsi) tanımlıyoruz
    is1 = HaritaIsi("Ahmet Bey'in Tarlası", "İfraz (Ayırma)", "105", "12")
    is2 = HaritaIsi("Belediye Park Alanı", "Tevhit (Birleştirme)", "240", "5")
    is3 = HaritaIsi("Yeni Site İnşaatı", "Plankote", "312", "1")
    is4 = HaritaIsi("Yol Genişletme Projesi", "Yola Terk", "50", "22")

    # İşleri bürolara dağıtıyoruz
    buro1.is_ata(is1)
    buro2.is_ata(is2)
    buro3.is_ata(is3)
    buro4.is_ata(is4)

    print("\n--- Büroların Güncel İş Durumları ---")
    for buro in buro_listesi:
        print(f"\n{buro.isim} İş Listesi:")
        if not buro.isler:
            print("  Henüz iş atanmamış.")
        for is_item in buro.isler:
            print(f"  - {is_item}")

if __name__ == "__main__":
    main()
