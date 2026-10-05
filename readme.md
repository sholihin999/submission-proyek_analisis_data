# ✨ Bike Sharing Dashboard ✨

Dashboard interaktif hasil analisis data **Bike Sharing Dataset (Capital Bikeshare, Washington D.C., 2011-2012)**, dibuat sebagai submission "Proyek Analisis Data" Dicoding.

## 📂 Struktur Direktori

```
submission
├───dashboard
│   ├───main_data.csv     # data per jam (hasil cleaning)
│   ├───day_data.csv      # data per hari (hasil cleaning)
│   └───dashboard.py
├───data
│   ├───day.csv
│   └───hour.csv
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt
```

## ⚙️ Setup Environment - Anaconda

```
conda create --name bike-sharing python=3.11
conda activate bike-sharing
pip install -r requirements.txt
```

## ⚙️ Setup Environment - Shell/Terminal (venv)

```
mkdir bike_sharing_dashboard
cd bike_sharing_dashboard
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 🚀 Menjalankan Dashboard di Lokal

Masuk ke folder `dashboard` lalu jalankan `streamlit run`:

```
cd dashboard
streamlit run dashboard.py
```

Dashboard akan otomatis terbuka di browser pada alamat `http://localhost:8501`.

## 🌐 Dashboard Online

Dashboard yang sudah di-deploy ke Streamlit Community Cloud dapat diakses melalui tautan pada berkas `url.txt`.

## 📓 Notebook Analisis

Seluruh proses analisis data (data wrangling, EDA, visualisasi, hingga kesimpulan) didokumentasikan lengkap pada `notebook.ipynb`. Notebook sudah dijalankan (executed) sehingga seluruh output dan visualisasi sudah tersimpan di dalamnya. Menjalankan ulang notebook dari folder `submission` akan menghasilkan kembali `dashboard/main_data.csv` dan `dashboard/day_data.csv`.

## 📊 Ringkasan Analisis

- **Pertanyaan 1:** Pengaruh musim & kondisi cuaca terhadap rata-rata penyewaan sepeda harian. Musim Panas tertinggi (±5.644/hari), Dingin terendah (±2.604/hari), dan cuaca hujan/salju menekan penyewaan hingga ±63% dibanding cuaca cerah.
- **Pertanyaan 2:** Pola penyewaan sepeda per jam pada hari kerja vs libur/akhir pekan. Hari kerja berpola bimodal (puncak ±08:00 dan 17:00-18:00), akhir pekan berpuncak di sekitar 12:00-15:00.
- **Analisis lanjutan:** Segmentasi manual (binning) waktu dalam sehari, disilangkan dengan tipe hari, untuk menentukan prioritas redistribusi armada.

## 🧹 Catatan Data Cleaning

- Nilai kelembapan (`hum`) = 0 yang tidak valid diganti melalui interpolasi berdasarkan urutan tanggal dan jam.
- Label musim disesuaikan dengan bulan sebenarnya pada data (kode 1 = Dingin, 2 = Semi, 3 = Panas, 4 = Gugur), karena pemetaan pada dokumentasi dataset tidak cocok dengan data.
- Kategori cuaca 4 (hujan lebat/salju) diberi label sendiri agar tidak hilang dari analisis.

## 🗂️ Sumber Data

Bike Sharing Dataset yang diberikan pihak dicoding, dimana berisi data penyewaan sepeda per jam (`hour.csv`) dan per hari (`day.csv`) di Washington D.C. pada tahun 2011-2012.
