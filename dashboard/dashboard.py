import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from pathlib import Path

sns.set_style("whitegrid")

# =============================================================================
# KONFIGURASI HALAMAN
# =============================================================================
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide",
)

SEASON_ORDER = ["Semi (Spring)", "Panas (Summer)", "Gugur (Fall)", "Dingin (Winter)"]
WEATHER_ORDER = ["Cerah/Berawan Sebagian", "Kabut/Berawan", "Hujan/Salju Ringan"]
TIME_OF_DAY_ORDER = ["Dini Hari (00-05)", "Pagi (06-09)", "Siang (10-14)", "Sore (15-18)", "Malam (19-23)"]

WEATHER_COLORS = {
    "Cerah/Berawan Sebagian": "#2E86AB",
    "Kabut/Berawan": "#A9A9A9",
    "Hujan/Salju Ringan": "#D64550",
}
DAYTYPE_COLORS = {"Hari Kerja": "#2E86AB", "Libur/Akhir Pekan": "#F2A541"}


# =============================================================================
# LOAD DATA
# =============================================================================
@st.cache_data
def load_data():
    path = Path(__file__).parent / "main_data.csv"
    df = pd.read_csv(path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    df["season_label"] = pd.Categorical(df["season_label"], categories=SEASON_ORDER, ordered=True)
    df["weathersit_label"] = pd.Categorical(df["weathersit_label"], categories=WEATHER_ORDER, ordered=True)
    df["time_of_day"] = pd.Categorical(df["time_of_day"], categories=TIME_OF_DAY_ORDER, ordered=True)
    return df


main_df = load_data()

# =============================================================================
# SIDEBAR - FILTER
# =============================================================================
st.sidebar.title("🚲 Filter Data")
st.sidebar.markdown("Gunakan filter berikut untuk mengeksplorasi data penyewaan sepeda.")

min_date, max_date = main_df["dteday"].min(), main_df["dteday"].max()
date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

season_filter = st.sidebar.multiselect(
    "Musim", options=SEASON_ORDER, default=SEASON_ORDER
)
weather_filter = st.sidebar.multiselect(
    "Kondisi Cuaca", options=WEATHER_ORDER, default=WEATHER_ORDER
)
daytype_filter = st.sidebar.multiselect(
    "Tipe Hari", options=["Hari Kerja", "Libur/Akhir Pekan"], default=["Hari Kerja", "Libur/Akhir Pekan"]
)

filtered_df = main_df[
    (main_df["dteday"] >= pd.to_datetime(start_date))
    & (main_df["dteday"] <= pd.to_datetime(end_date))
    & (main_df["season_label"].isin(season_filter))
    & (main_df["weathersit_label"].isin(weather_filter))
    & (main_df["workingday_label"].isin(daytype_filter))
]

st.sidebar.markdown("---")
st.sidebar.caption("Sumber data: Capital Bikeshare, Washington D.C. (2011-2012)")

# =============================================================================
# HEADER & KPI
# =============================================================================
st.title("🚲 Bike Sharing Dashboard")
st.markdown("Dashboard interaktif untuk menjawab pertanyaan bisnis seputar **pengaruh musim/cuaca** dan **pola penyewaan per jam** pada layanan bike-sharing (2011-2012).")

if filtered_df.empty:
    st.warning("Tidak ada data pada kombinasi filter ini. Silakan ubah filter di sidebar.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Penyewaan", f"{filtered_df['cnt'].sum():,}")
col2.metric("Rata-rata per Jam", f"{filtered_df['cnt'].mean():,.0f}")
col3.metric("Kontribusi Registered", f"{filtered_df['registered'].sum() / filtered_df['cnt'].sum():.1%}")
col4.metric("Kontribusi Casual", f"{filtered_df['casual'].sum() / filtered_df['cnt'].sum():.1%}")

st.markdown("---")

# =============================================================================
# PERTANYAAN 1: MUSIM & CUACA
# =============================================================================
st.header("Pertanyaan 1: Pengaruh Musim & Cuaca")
st.markdown(
    "Bagaimana pengaruh musim dan kondisi cuaca terhadap rata-rata jumlah penyewaan sepeda?"
)

c1, c2 = st.columns([3, 2])

with c1:
    agg = (
        filtered_df.groupby(["season_label", "weathersit_label"], observed=True)["cnt"]
        .mean()
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=agg, x="season_label", y="cnt", hue="weathersit_label",
        order=[s for s in SEASON_ORDER if s in agg["season_label"].unique()],
        hue_order=[w for w in WEATHER_ORDER if w in agg["weathersit_label"].unique()],
        palette=WEATHER_COLORS, ax=ax,
    )
    ax.set_title("Rata-rata Penyewaan per Musim & Kondisi Cuaca", weight="bold")
    ax.set_xlabel("Musim")
    ax.set_ylabel("Rata-rata Jumlah Penyewaan (cnt)")
    ax.legend(title="Kondisi Cuaca", fontsize=8)
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)

with c2:
    st.markdown("**Rata-rata penyewaan per musim**")
    st.dataframe(
        filtered_df.groupby("season_label", observed=True)["cnt"].mean().round(0).reindex(
            [s for s in SEASON_ORDER if s in filtered_df["season_label"].unique()]
        ),
        use_container_width=True,
    )
    st.markdown("**Rata-rata penyewaan per cuaca**")
    st.dataframe(
        filtered_df.groupby("weathersit_label", observed=True)["cnt"].mean().round(0).reindex(
            [w for w in WEATHER_ORDER if w in filtered_df["weathersit_label"].unique()]
        ),
        use_container_width=True,
    )

st.info(
    "💡 **Insight:** Cuaca cerah selalu menghasilkan penyewaan tertinggi di setiap musim, sementara cuaca "
    "hujan/salju menekan penyewaan secara drastis. Musim Gugur & Panas menjadi periode permintaan tertinggi, "
    "sedangkan Semi terendah."
)

st.markdown("---")

# =============================================================================
# PERTANYAAN 2: POLA PER JAM
# =============================================================================
st.header("Pertanyaan 2: Pola Penyewaan per Jam")
st.markdown(
    "Bagaimana pola jumlah penyewaan sepeda per jam berbeda antara hari kerja dan libur/akhir pekan?"
)

hourly = (
    filtered_df.groupby(["hr", "workingday_label"], observed=True)["cnt"]
    .mean()
    .reset_index()
)
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.lineplot(
    data=hourly, x="hr", y="cnt", hue="workingday_label",
    marker="o", palette=DAYTYPE_COLORS, ax=ax2,
)
ax2.set_title("Rata-rata Penyewaan per Jam: Hari Kerja vs Libur/Akhir Pekan", weight="bold")
ax2.set_xlabel("Jam (0-23)")
ax2.set_ylabel("Rata-rata Jumlah Penyewaan (cnt)")
ax2.set_xticks(range(0, 24))
ax2.legend(title="")
sns.despine()
plt.tight_layout()
st.pyplot(fig2)

st.info(
    "💡 **Insight:** Hari kerja menunjukkan pola bimodal (puncak pagi ~08:00 & sore 17:00-18:00) khas commuting, "
    "sementara libur/akhir pekan menunjukkan pola unimodal yang landai dengan puncak di sekitar tengah hari."
)

st.markdown("---")

# =============================================================================
# ANALISIS LANJUTAN: BINNING / MANUAL GROUPING
# =============================================================================
st.header("Analisis Lanjutan: Segmentasi Waktu (Binning)")
st.markdown(
    "Segmentasi manual (*binning*, tanpa algoritma machine learning) berdasarkan 5 kelompok waktu, "
    "disilangkan dengan tipe hari, untuk menentukan prioritas redistribusi armada."
)

segment = (
    filtered_df.groupby(["time_of_day", "workingday_label"], observed=True)["cnt"]
    .mean()
    .unstack()
    .reindex([t for t in TIME_OF_DAY_ORDER if t in filtered_df["time_of_day"].unique()])
)

fig3, ax3 = plt.subplots(figsize=(8, 4.5))
sns.heatmap(segment, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax3, cbar_kws={"label": "Rata-rata cnt"})
ax3.set_title("Rata-rata Penyewaan per Segmen Waktu x Tipe Hari", weight="bold")
ax3.set_xlabel("")
ax3.set_ylabel("Segmen Waktu")
plt.tight_layout()
st.pyplot(fig3)

st.success(
    "✅ **Rekomendasi Action Item:** Prioritaskan redistribusi armada menjelang jam sibuk (07:00-09:00 & "
    "17:00-19:00 hari kerja, 12:00-15:00 akhir pekan), dan manfaatkan jendela Dini Hari sebagai waktu maintenance "
    "karena permintaan pada segmen ini paling rendah."
)

st.caption("Dashboard ini dibangun dari submission proyek analisis data")
