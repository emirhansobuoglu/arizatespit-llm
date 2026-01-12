import csv
import re

INPUT_CSV = "cevaplar.csv"
OUTPUT_CSV = "temiz_cevaplar.csv"

UNWANTED_PATTERNS = [
    r"\d{1,2}\s\w+\s20\d{2}\s\d{2}:\d{2}:\d{2}\sMesaj Linkini Kopyala Şikayet",
    r"Mesaj Linkini Kopyala Şikayet",
]

def clean_text(text):
    if not text:
        return ""

    for pattern in UNWANTED_PATTERNS:
        text = re.sub(pattern, "", text)

    text = re.sub(r"\s+", " ", text).strip()
    return text

cleaned_rows = []

with open(INPUT_CSV, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames

    for row in reader:

        # --- Metin temizliği ---
        baslik = clean_text(row.get("baslik", ""))
        sorun = clean_text(row.get("sorun", ""))
        cevaplar = clean_text(row.get("cevaplar", ""))

        # --- Boş satırları atla ---
        if not baslik or not sorun or not cevaplar:
            continue  # Bu satırı tamamen sil

        cleaned_rows.append({
            "baslik": baslik,
            "sorun": sorun,
            "cevaplar": cevaplar
        })

with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cleaned_rows)

print(f"Temizleme tamamlandı! Çıktı dosyası: {OUTPUT_CSV}")
print(f"Toplam kalan satır: {len(cleaned_rows)}")
