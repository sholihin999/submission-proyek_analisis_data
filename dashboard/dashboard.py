import pandas as pd
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
WEATHER_ORDER_DAY = ["Cerah/Berawan Sebagian", "Kabut/Berawan", "Hujan/Salju Ringan"]
WEATHER_ORDER_HOUR = WEATHER_ORDER_DAY + ["Hujan Lebat/Salju"]
TIME_OF_DAY_ORDER = ["Dini Hari (00-05)", "Pagi (06-09)", "Siang (10-14)", "Sore (15-18)", "Malam (19-23)"]
DAYTYPE_ORDER = ["Hari Kerja", "Libur/Akhir Pekan"]

WEATHER_COLORS = {
    "Cerah/Berawan Sebagian": "#2E86AB",
    "Kabut/Berawan": "#A9A9A9",
    "Hujan/Salju Ringan": "#D64550",
}
DAYTYPE_COLORS = {"Hari Kerja": "#2E86AB", "Libur/Akhir Pekan": "#F2A541"}

DATA_DIR = Path(__file__).parent


# =============================================================================
# LOAD DATA
# =============================================================================
@st.cache_data
def load_data():
    """Muat data per jam (main_data.csv) dan data per hari (day_data.csv)."""
    hour = pd.read_csv(DATA_DIR / "main_data.csv")
    day = pd.read_csv(DATA_DIR / "day_data.csv")
    for df, weather_order in ((hour, WEATHER_ORDER_HOUR), (day, WEATHER_ORDER_DAY)):
        df["dteday"] = pd.to_datetime(df["dteday"])
        df["season_label"] = pd.Categorical(df["season_label"], categories=SEASON_ORDER, ordered=True)
        df["weathersit_label"] = pd.Categorical(df["weathersit_label"], categories=weather_order, ordered=True)
    hour["time_of_day"] = pd.Categorical(hour["time_of_day"], categories=TIME_OF_DAY_ORDER, ordered=True)
    return hour, day


hour_df, day_df = load_data()

# =============================================================================
# SIDEBAR - FILTER
# =============================================================================
st.sidebar.title("🚲 Filter Data")
st.sidebar.markdown("Gunakan filter berikut untuk mengeksplorasi data penyewaan sepeda.")

min_date, max_date = hour_df["dteday"].min().date(), hour_df["dteday"].max().date()
date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

season_filter = st.sidebar.multiselect("Musim", options=SEASON_ORDER, default=SEASON_ORDER)
weather_filter = st.sidebar.multiselect("Kondisi Cuaca", options=WEATHER_ORDER_HOUR, default=WEATHER_ORDER_HOUR)
daytype_filter = st.sidebar.multiselect("Tipe Hari", options=DAYTYPE_ORDER, default=DAYTYPE_ORDER)


def apply_filters(df):
    return df[
        (df["dteday"] >= pd.to_datetime(start_date))
        & (df["dteday"] <= pd.to_datetime(end_date))
        & (df["season_label"].isin(season_filter))
        & (df["weathersit_label"].isin(weather_filter))
        & (df["workingday_label"].isin(daytype_filter))
    ]


filtered_hour = apply_filters(hour_df)
filtered_day = apply_filters(day_df)

st.sidebar.markdown("---")
st.sidebar.caption("Sumber data: Capital Bikeshare, Washington D.C. (2011-2012)")

# =============================================================================
# HEADER & KPI
# =============================================================================
st.title("🚲 Bike Sharing Dashboard")
st.markdown(
    "Dashboard interaktif untuk menjawab pertanyaan bisnis seputar **pengaruh musim/cuaca** dan "
    "**pola penyewaan per jam** pada layanan bike-sharing (2011-2012)."
)

if filtered_hour.empty or filtered_day.empty:
    st.warning("Tidak ada data pada kombinasi filter ini. Silakan ubah filter di sidebar.")
    st.stop()

total_cnt = filtered_hour["cnt"].sum()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Penyewaan", f"{total_cnt:,}")
col2.metric("Rata-rata per Hari", f"{filtered_day['cnt'].mean():,.0f}")
col3.metric("Kontribusi Registered", f"{filtered_hour['registered'].sum() / total_cnt:.1%}")
col4.metric("Kontribusi Casual", f"{filtered_hour['casual'].sum() / total_cnt:.1%}")

st.markdown("---")

# =============================================================================
# PERTANYAAN 1: MUSIM & CUACA
# =============================================================================
st.header("Pertanyaan 1: Pengaruh Musim & Cuaca")
st.markdown(
    "Bagaimana pengaruh musim dan kondisi cuaca terhadap rata-rata jumlah penyewaan sepeda **harian** "
    "sepanjang 2011-2012, dan kombinasi musim-cuaca mana yang paling perlu diantisipasi?"
)

c1, c2 = st.columns([3, 2])

with c1:
    agg = (
        filtered_day.groupby(["season_label", "weathersit_label"], observed=True)["cnt"]
        .mean()
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=agg, x="season_label", y="cnt", hue="weathersit_label",
        order=[s for s in SEASON_ORDER if s in agg["season_label"].unique()],
        hue_order=[w for w in WEATHER_ORDER_DAY if w in agg["weathersit_label"].unique()],
        palette=WEATHER_COLORS, errorbar=None, ax=ax,
    )
    ax.set_title("Rata-rata Penyewaan Harian per Musim & Kondisi Cuaca", weight="bold")
    ax.set_xlabel("Musim")
    ax.set_ylabel("Rata-rata Penyewaan per Hari (cnt)")
    ax.legend(title="Kondisi Cuaca", fontsize=8)
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)

with c2:
    st.markdown("**Rata-rata penyewaan per hari, per musim**")
    st.dataframe(
        filtered_day.groupby("season_label", observed=True)["cnt"].mean().round(0)
        .reindex([s for s in SEASON_ORDER if s in filtered_day["season_label"].unique()])
        .rename("Rata-rata cnt/hari")
    )
    st.markdown("**Rata-rata penyewaan per hari, per cuaca**")
    st.dataframe(
        filtered_day.groupby("weathersit_label", observed=True)["cnt"].mean().round(0)
        .reindex([w for w in WEATHER_ORDER_DAY if w in filtered_day["weathersit_label"].unique()])
        .rename("Rata-rata cnt/hari")
    )

st.info(
    "💡 **Insight (seluruh data 2011-2012):** Musim Panas mencatat permintaan tertinggi (±5.644/hari), diikuti "
    "Semi dan Gugur, sedangkan Dingin terendah (±2.604/hari). Di setiap musim, cuaca cerah menghasilkan "
    "penyewaan tertinggi dan hujan/salju menekan penyewaan secara drastis (rata-rata ±63% lebih rendah "
    "dibanding cuaca cerah)."
)

st.markdown("---")

# =============================================================================
# PERTANYAAN 2: POLA PER JAM
# =============================================================================
st.header("Pertanyaan 2: Pola Penyewaan per Jam")
st.markdown(
    "Bagaimana pola jumlah penyewaan sepeda per jam berbeda antara hari kerja dan libur/akhir pekan "
    "sepanjang 2011-2012, dan pada rentang jam berapa terjadi puncak permintaan?"
)

hourly = (
    filtered_hour.groupby(["hr", "workingday_label"], observed=True)["cnt"]
    .mean()
    .reset_index()
)
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.lineplot(
    data=hourly, x="hr", y="cnt", hue="workingday_label",
    hue_order=[d for d in DAYTYPE_ORDER if d in hourly["workingday_label"].unique()],
    marker="o", palette=DAYTYPE_COLORS, errorbar=None, ax=ax2,
)
ax2.axvspan(7, 9, color="grey", alpha=0.08)
ax2.axvspan(17, 19, color="grey", alpha=0.08)
ax2.set_title("Rata-rata Penyewaan per Jam: Hari Kerja vs Libur/Akhir Pekan", weight="bold")
ax2.set_xlabel("Jam (0-23)")
ax2.set_ylabel("Rata-rata Penyewaan per Jam (cnt)")
ax2.set_xticks(range(0, 24))
ax2.set_ylim(bottom=0)
ax2.legend(title="")
sns.despine()
plt.tight_layout()
st.pyplot(fig2)

st.info(
    "💡 **Insight (seluruh data 2011-2012):** Hari kerja menunjukkan pola bimodal khas commuting (puncak pagi "
    "±08:00 dan sore 17:00-18:00, hingga ±525 penyewaan/jam), sementara libur/akhir pekan menunjukkan pola "
    "unimodal yang landai dengan puncak di sekitar 12:00-15:00 (±373 penyewaan/jam)."
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
    filtered_hour.groupby(["time_of_day", "workingday_label"], observed=True)["cnt"]
    .mean()
    .unstack()
    .reindex([t for t in TIME_OF_DAY_ORDER if t in filtered_hour["time_of_day"].unique()])
)

fig3, ax3 = plt.subplots(figsize=(8, 4.5))
sns.heatmap(segment, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax3, cbar_kws={"label": "Rata-rata cnt per jam"})
ax3.set_title("Rata-rata Penyewaan per Segmen Waktu x Tipe Hari", weight="bold")
ax3.set_xlabel("")
ax3.set_ylabel("Segmen Waktu")
plt.tight_layout()
st.pyplot(fig3)

st.success(
    "✅ **Rekomendasi Action Item:** Prioritaskan redistribusi armada menjelang jam sibuk (07:00-09:00 & "
    "17:00-19:00 hari kerja, 12:00-15:00 akhir pekan), dan manfaatkan jendela Dini Hari sebagai waktu "
    "maintenance karena permintaan pada segmen ini paling rendah."
)

st.caption("Dashboard ini dibangun sebagai bagian dari submission Proyek Analisis Data (Dicoding).")
