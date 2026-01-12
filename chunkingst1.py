import pandas as pd
from nltk.tokenize import sent_tokenize
import nltk

nltk.download('punkt')
nltk.download('punkt_tab')

df = pd.read_csv("temiz_cevaplar.csv")

chunks = []


def split_long_text(text, max_tokens=200):
    """Uzun cevapları küçük parçalara böler."""
    sentences = sent_tokenize(text)
    current = ""
    parts = []

    for sent in sentences:
        if len((current + " " + sent).split()) > max_tokens:
            parts.append(current.strip())
            current = sent
        else:
            current += " " + sent

    if current.strip():
        parts.append(current.strip())

    return parts


for idx, row in df.iterrows():
    baslik = str(row['baslik'])
    sorun = str(row['sorun'])

    # cevapları ||| ile ayır
    cevaplar = str(row['cevaplar']).split("|||")

    for cevap in cevaplar:
        cevap = cevap.strip()
        if len(cevap) < 5:
            continue

        # Eğer cevap aşırı uzunsa parçalara ayır
        cevap_parcalar = split_long_text(cevap, max_tokens=120)

        for cp in cevap_parcalar:
            chunk_text = f"Başlık: {baslik}\nSorun: {sorun}\nCevap: {cp}"
            chunks.append(chunk_text)

print("Toplam chunk sayısı:", len(chunks))
print("Örnek chunk:\n", chunks[0])
