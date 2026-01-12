# icerik.py (uyumlu + gelişmiş)
import csv
import requests
from bs4 import BeautifulSoup
from time import sleep
from urllib.parse import urljoin, urlparse
import re

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

KONULAR_CSV = "konular.csv"
OUT_CSV = "cevaplar.csv"


# ---------------------------------------------------
#   GELİŞMİŞ TEMİZLEME FONKSİYONU
# ---------------------------------------------------
def clean_text(s):
    """Mesajları temizle, quote kalıntılarını sil, gereksiz meta/şablonları çıkar."""
    if not s:
        return ""

    # çoklu boşlukları düzelt
    s = re.sub(r'\s+', ' ', s).strip()

    # mesaj linki – şikayet – meta
    s = re.sub(r'Mesaj Linkini Kopyala.*?', '', s, flags=re.I)
    s = re.sub(r'Şikayet.*?', '', s, flags=re.I)

    # gizli DH meta mesajları
    s = re.sub(r'< Bu mesaj .*?>', '', s)
    s = re.sub(r'Bu mesaj bir yönetici tarafından.*', '', s)

    # quote kalıntıları
    s = re.sub(r'.*Alıntı.*', '', s)

    # link temizliği
    s = re.sub(r'http\S+', '', s)

    # çok uzun aşırı hikayeleri filtrele (spam önleme)
    if len(s) > 1200:
        return ""

    return s.strip()


# ---------------------------------------------------
#   SAYFALANDIRMA TESPİTİ (ESKİYLE UYUMLU)
# ---------------------------------------------------
def get_thread_pages(soup, base_url):
    pages = set([base_url])

    selectors = [
        "div.topic-pages a",
        "div.paging a",
        "div.paginator a",
        "ul.pagination a",
        "nav.pagination a",
        "div.sayfalar a",
    ]

    for sel in selectors:
        for a in soup.select(sel):
            href = a.get("href")
            if not href:
                continue
            full = urljoin(base_url, href)
            if urlparse(full).path.startswith(urlparse(base_url).path):
                pages.add(full)

    pages = list(pages)
    pages.sort()
    return pages


# ---------------------------------------------------
#   QUOTE (ALINTI) TEMİZLEYİCİ – YENİ EKLENDİ
# ---------------------------------------------------
def remove_quotes(block):
    """DH forum quote bölümlerini tamamen DOM'dan söker."""
    for q in block.select(".quote"):
        q.decompose()
    for q in block.select(".msg-quote"):
        q.decompose()
    return block


# ---------------------------------------------------
#   MESAJ AYIKLAMA (ESKİYLE UYUMLU + GELİŞTİRİLMİŞ)
# ---------------------------------------------------
def extract_messages_from_soup(soup):
    messages = []

    # Önce bilinen DH mesaj kutularını dene
    candidates = []
    candidates += soup.select("span.msg")

    # duplicate blokları engelle
    seen_blocks = set()
    filtered_blocks = []

    for c in candidates:
        key = str(c)[:200]
        if key not in seen_blocks:
            seen_blocks.add(key)
            filtered_blocks.append(c)

    # her bloktan gerçek mesajları al
    for block in filtered_blocks:
        block = remove_quotes(block)  # *** önemli yeni adım ***

        td = block.find("td")
        if td:
            text = td.get_text(separator=" ", strip=True)
        else:
            text = block.get_text(separator=" ", strip=True)

        text = clean_text(text)

        if text and len(text) > 3:
            messages.append(text)

    # tekrar eden metinleri sil
    unique = []
    seen = set()

    for m in messages:
        if m not in seen:
            seen.add(m)
            unique.append(m)

    return unique


# ---------------------------------------------------
#   THREAD PARSE FONKSİYONU (ESKİYLE AYNI)
# ---------------------------------------------------
def parse_thread(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
    except Exception as e:
        print(f"❌ {url} yüklenemedi: {e}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    pages = get_thread_pages(soup, url)
    all_msgs = []

    for page_url in pages:
        try:
            r2 = requests.get(page_url, headers=HEADERS, timeout=12)
            r2.raise_for_status()
        except Exception as e:
            print(f"⚠️ Sayfa yüklenemedi: {page_url}")
            continue

        soup2 = BeautifulSoup(r2.text, "html.parser")
        msgs = extract_messages_from_soup(soup2)

        for m in msgs:
            if m not in all_msgs:
                all_msgs.append(m)

        sleep(0.4)

    return all_msgs


# ---------------------------------------------------
#   CSV'DEN KONULARI OKU (ESKİYLE AYNI)
# ---------------------------------------------------
def load_topics_from_csv(path):
    topics = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            baslik = row.get("Başlık")
            link = row.get("Link")
            if baslik and link:
                topics.append({"baslik": baslik, "link": link})
    return topics


# ---------------------------------------------------
#   ANA PROGRAM
# ---------------------------------------------------
def main():
    topics = load_topics_from_csv(KONULAR_CSV)
    print(f"Toplam {len(topics)} konu bulundu.\n")

    rows = []

    for i, t in enumerate(topics, 1):
        print(f"[{i}/{len(topics)}] İşleniyor → {t['baslik']}")
        msgs = parse_thread(t["link"])

        if not msgs:
            print("⚠️ Mesaj alınamadı.\n")
            continue

        sorun = msgs[0]
        cevaplar = msgs[1:]

        rows.append({
            "baslik": t["baslik"],
            "sorun": sorun,
            "cevaplar": " ||| ".join(cevaplar)
        })

        print(f"   ✔ Toplam mesaj: {len(msgs)}\n")
        sleep(1)

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["baslik", "sorun", "cevaplar"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"\n💾 Tamamlandı → {OUT_CSV}")


if __name__ == "__main__":
    main()
