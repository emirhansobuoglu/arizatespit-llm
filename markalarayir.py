import pandas as pd
import os

# Girdi dosyası
GIRDI_DOSYA = "temiz_cevaplar.csv"

# Çıktı klasörü
CIKTI_KLASOR = "veri"
os.makedirs(CIKTI_KLASOR, exist_ok=True)

# Aranacak marka isimleri
MARKALAR = [
    "bosch", "arçelik", "beko", "siemens", "samsung", "lg", "vestel",
    "profilo", "grundig", "altus", "sharp", "mitsubishi", "daewoo",
    "electrolux", "candy", "hoover", "seg", "indesit"
]

df = pd.read_csv(GIRDI_DOSYA)

# Küçük harfe çevir (arama için)
df["baslik_lower"] = df["baslik"].str.lower()
df["sorun_lower"] = df["sorun"].str.lower()

# Marka bazlı ayırma
for marka in MARKALAR:
    mask = df["baslik_lower"].str.contains(marka, na=False) | df["sorun_lower"].str.contains(marka, na=False)
    marka_df = df[mask].copy()

    if not marka_df.empty:
        # Gereksiz sütunları çıkar
        marka_df = marka_df[["baslik", "sorun", "cevaplar"]]

        # Dosya adı oluştur
        dosya_adi = os.path.join(CIKTI_KLASOR, f"{marka}.csv")

        # Kaydet
        marka_df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")
        print(f"✅ {marka.title()} için {len(marka_df)} kayıt kaydedildi → {dosya_adi}")
    else:
        print(f"⚪ {marka.title()} için kayıt bulunamadı.")

print("\n🎯 İşlem tamamlandı! Bütün markalar /veri klasörüne kaydedildi.")
