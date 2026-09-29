import pandas as pd
import sqlite3
import streamlit as st

# Konfigurasi Halaman Dashboard
st.set_page_config(
    page_title="Dashboard Laporan Keuangan", page_icon="💰", layout="wide"
)

# 1. Hubungkan Python ke Database SQLite (file keuangan.db)
try:
  conn = sqlite3.connect("keuangan.db")
except Exception as e:
  st.error(f"Gagal terhubung ke database SQLite: {e}")
  st.stop()

# 2. Ambil Data dari Tabel SQLite menggunakan Pandas
query = "SELECT * FROM transaksi"
df = pd.read_sql(query, conn)
conn.close()

# Judul Dashboard
st.title("📊 Dashboard Laporan Keuangan Perusahaan")
st.markdown("---")

# Cek apakah data kosong
if df.empty:
  st.warning(
      "Belum ada data di dalam tabel database. Silakan masukkan data terlebih"
      " dahulu."
  )
else:
  # Ubah kolom tanggal ke format datetime
  df["tanggal"] = pd.to_datetime(df["tanggal"])

  # 3. Hitung Metrik Utama (KPI Cards)
  total_pendapatan = df[df["jenis_transaksi"] == "Pemasukan"]["jumlah"].sum()
  total_pengeluaran = df[df["jenis_transaksi"] == "Pengeluaran"]["jumlah"].sum()
  laba_bersih = total_pendapatan - total_pengeluaran

  # Tampilkan dalam bentuk kolom kartu metrik di Streamlit
  col1, col2, col3 = st.columns(3)
  col1.metric("💵 Total Pendapatan", f"Rp {total_pendapatan:,.0f}")
  col2.metric("💸 Total Pengeluaran", f"Rp {total_pengeluaran:,.0f}")
  col3.metric(
      "📈 Laba Bersih",
      f"Rp {laba_bersih:,.0f}",
      delta=("Sehat" if laba_bersih >= 0 else "Defisit"),
  )

  st.markdown("---")

  # 4. Tampilkan Grafik & Tabel Pendukung
  col_grafik1, col_grafik2 = st.columns(2)

  with col_grafik1:
    st.subheader("📅 Tren Keuangan Berdasarkan Tanggal")
    chart_data = (
        df.groupby(["tanggal", "jenis_transaksi"])["jumlah"]
        .sum()
        .unstack()
        .fillna(0)
    )
    st.line_chart(chart_data)

  with col_grafik2:
    st.subheader("🏷️ Rincian Pengeluaran per Kategori")
    df_pengeluaran = df[df["jenis_transaksi"] == "Pengeluaran"]
    if not df_pengeluaran.empty:
      kategori_exp = df_pengeluaran.groupby("kategori")["jumlah"].sum()
      st.bar_chart(kategori_exp)
    else:
      st.info("Belum ada data pengeluaran.")

  # 5. Tampilkan Tabel Data Mentah
  st.subheader("📋 Riwayat Transaksi Lengkap")
  st.dataframe(df, use_container_width=True)