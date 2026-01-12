import pandas as pd

df = pd.read_csv("temiz_cevaplar.csv")


def fixed_overlap(text, chunk_size=512, overlap=128):
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        if not chunk_words:
            break

        chunks.append(" ".join(chunk_words))
        start += (chunk_size - overlap)

    return chunks


chunks_strategy2 = []

for idx, row in df.iterrows():
    baslik = str(row['baslik'])
    sorun = str(row['sorun'])
    cevaplar = str(row['cevaplar']).replace("|||", " ")  # hepsini tek metne çevir

    full_text = f"Başlık: {baslik}\nSorun: {sorun}\nCevaplar: {cevaplar}"

    small_chunks = fixed_overlap(full_text, chunk_size=512, overlap=128)

    for c in small_chunks:
        chunks_strategy2.append(c)

print("STRATEJİ 2 - Fixed+Overlap chunk sayısı:", len(chunks_strategy2))
print("\nÖrnek chunk:\n", chunks_strategy2[0])
