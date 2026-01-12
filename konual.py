import csv
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://forum.donanimhaber.com/buzdolaplari--f756?sayfa={}"
CSV_FILE = "konular.csv"
MIN_REPLIES = 3

# SADECE problem içeren konuları bulmak için anahtar kelimeler (EN AZ BİRİ OLACAK)
PROBLEM_STEMS = [
    "arız", "sorun", "problem", "bozul", "tamir", "karlan", "buzlan",
    "akıtıyo", "damlatıyo", "koku", "gürültü", "uğultu", "tüketim",
    "soğutmu", "donmu", "ısınma", "kompresör", "fan", "motor",
    "patla", "değişim", "şikayet", "servis", "garanti", "ses"
]

# Yasaklı kelimeler (Problem olmayan, genel konuları elemek için)
BANNED_WORDS = ["reklam", "kampanya", "haber", "satış", "fiyat", "indirim", "tavsiye", "incelemesi", "öneri"]

# ----------------- YENİ KONTROL YAPILARI -----------------
KAYDEDILENLER = []  # (başlık, link) tutan nihai liste
EKLENEN_LINKLER = set()  # Tekrarlayan linkleri kontrol etmek için set yapısı
# --------------------------------------------------------

tekrar = 0
for sayfa in range(1, 100, 2):
    url = BASE_URL.format(sayfa)
    print(f"📄 Sayfa {sayfa} çekiliyor: {url}")
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    sayi=0

    konular = soup.select("div.kl-icerik-satir.yenikonu")
    print(f"  ➤ {len(konular)} konu bulundu")

    for konu in konular:
        # Başlık ve href
        a_tag = konu.select_one("div.kl-konu a")
        if not a_tag:
            print("    ⚠️ Konu için href bulunamadı, atlanıyor.")
            continue

        baslik = a_tag.get_text(strip=True)
        href = a_tag.get("href")
        if not href.startswith("http"):
            href = "https://forum.donanimhaber.com" + href

        # ----------------- TEKRAR KONTROLÜ (YENİ KONTROL) -----------------
        if href in EKLENEN_LINKLER:
            tekrar +=1
            print(f"    🔄 Tekrarlanan konu atlandı: {baslik}")
            continue
        # ------------------------------------------------------------------

        # Cevap sayısı
        cevap_span = konu.select_one("div.kl-cevap span")
        try:
            cevap = int(cevap_span.get_text(strip=True))
        except:
            cevap = 0

        if cevap < MIN_REPLIES:
            continue

        baslik_lower = baslik.lower()
        # 2. PROBLEM KÖK KONTROLÜ (Başlığın herhangi bir yerinde kök geçiyor mu?)
        is_problem = any(kok in baslik_lower for kok in PROBLEM_STEMS)

        if not is_problem:
            continue  # Problem kökü yoksa ATLA

        # Yasaklı Kelime Filtresi (HİÇBİRİ OLMAMALI)
        if any(k.lower() in baslik.lower() for k in BANNED_WORDS):
            continue

        # Konuyu kaydet
        KAYDEDILENLER.append((baslik, href))
        sayi +=1
        EKLENEN_LINKLER.add(href)  # Linki set'e ekle
    print(f"\n   {sayi} konu kaydedildi.")

# CSV kaydet
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Başlık", "Link"])
    writer.writerows(KAYDEDILENLER)

print(f"\n✅ Toplam {len(KAYDEDILENLER)} benzersiz sorun konusu kaydedildi → {CSV_FILE}, Tekrar : {tekrar}")