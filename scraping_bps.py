import pandas as pd
import requests
from io import StringIO

url = "https://www.bps.go.id/id/statistics-table/2/MTQ5OCMy/luas-panen--produksi--dan-produktivitas-padi-menurut-provinsi.html"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Ambil HTML dengan headers biar nggak kena 403
response = requests.get(url, headers=headers, timeout=30)
response.raise_for_status()

# Ambil semua tabel dari HTML
tables = pd.read_html(StringIO(response.text))

# Biasanya tabel utama ada di index 0
df = tables[0]

print("Kolom asli:")
print(df.columns)

# Kalau header bertingkat (MultiIndex), gabungkan jadi satu nama kolom
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [
        " ".join([str(x).strip() for x in col if str(x) != "nan"]).strip()
        for col in df.columns
    ]
else:
    df.columns = [str(c).strip() for c in df.columns]

print("\nKolom setelah dirapikan:")
for c in df.columns:
    print(c)

# Cari kolom nama provinsi
prov_col = None
for c in df.columns:
    cl = c.lower()
    if "provinsi" in cl or "38 provinsi" in cl:
        prov_col = c
        break

if prov_col is None:
    prov_col = df.columns[0]  # fallback

# Cari kolom Luas Panen 2020
luas_col = None
for c in df.columns:
    cl = c.lower()
    if "luas panen" in cl and "2020" in cl:
        luas_col = c
        break

# Cari kolom Produksi 2020
produksi_col = None
for c in df.columns:
    cl = c.lower()
    if "produksi" in cl and "2020" in cl:
        produksi_col = c
        break

print("\nKolom terpilih:")
print("Provinsi:", prov_col)
print("Luas Panen 2020:", luas_col)
print("Produksi 2020:", produksi_col)

if luas_col is None or produksi_col is None:
    raise ValueError("Kolom 2020 tidak ketemu. Cek output nama kolom di terminal.")

# Buat data terpisah
df_luas_2020 = df[[prov_col, luas_col]].copy()
df_luas_2020.columns = ["Provinsi", "Luas_Panen_2020"]

df_produksi_2020 = df[[prov_col, produksi_col]].copy()
df_produksi_2020.columns = ["Provinsi", "Produksi_2020"]

# Bersihkan angka Indonesia format: 317.869,41 -> 317869.41
def clean_id_number(series):
    return (
        series.astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.extract(r"(-?\d+\.?\d*)")[0]
        .astype(float)
    )

df_luas_2020["Luas_Panen_2020"] = clean_id_number(df_luas_2020["Luas_Panen_2020"])
df_produksi_2020["Produksi_2020"] = clean_id_number(df_produksi_2020["Produksi_2020"])

# Simpan file terpisah
df_luas_2020.to_csv("luas_panen_padi_2020.csv", index=False, encoding="utf-8-sig")
df_produksi_2020.to_csv("produksi_padi_2020.csv", index=False, encoding="utf-8-sig")

print("\nBerhasil simpan:")
print("- luas_panen_padi_2020.csv")
print("- produksi_padi_2020.csv")