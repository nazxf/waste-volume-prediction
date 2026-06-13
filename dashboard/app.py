"""
Streamlit Dashboard for Waste Volume Prediction System
Interactive web application for waste volume forecasting and analysis
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import joblib
from iot_storage import get_latest_readings

# Import custom modules
try:
    from export import export_predictions_to_excel, export_predictions_to_pdf
    from predict import WasteVolumePredictor
    PREDICTOR_AVAILABLE = True
except:
    PREDICTOR_AVAILABLE = False


# Page configuration
st.set_page_config(
    page_title="Waste Volume Prediction System",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_dataset():
    """Load dataset from CSV"""
    project_root = Path(__file__).parent.parent
    data_path = project_root / "data" / "raw" / "waste_dataset.csv"
    
    if data_path.exists():
        df = pd.read_csv(data_path)
        df['date'] = pd.to_datetime(df['date'])
        return df
    return None


@st.cache_resource
def load_predictor():
    """Load predictor model"""
    if PREDICTOR_AVAILABLE:
        try:
            predictor = WasteVolumePredictor()
            return predictor
        except FileNotFoundError:
            return None
    return None


def page_dashboard():
    """Main Dashboard Page"""
    st.markdown('<div class="main-header">♻️ Sistem Prediksi Volume Sampah Kota</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Optimasi Pengangkutan Sampah dengan Machine Learning</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_dataset()
    predictor = load_predictor()
    
    if df is None:
        st.error("❌ Dataset tidak ditemukan. Jalankan `python src/train_model.py` terlebih dahulu.")
        return
    
    if predictor is None:
        st.warning("⚠️ Model belum tersedia. Jalankan `python src/train_model.py` untuk melatih model.")
        return
    
    # Key Metrics
    st.subheader("📊 Statistik Utama")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_waste = df['waste_volume'].mean()
        st.metric("Rata-rata Volume Harian", f"{avg_waste:.2f} ton")
    
    with col2:
        total_days = len(df)
        st.metric("Total Data Harian", f"{total_days:,} hari")
    
    with col3:
        max_waste = df['waste_volume'].max()
        st.metric("Volume Maksimum", f"{max_waste:.2f} ton")
    
    with col4:
        min_waste = df['waste_volume'].min()
        st.metric("Volume Minimum", f"{min_waste:.2f} ton")
    
    st.markdown("---")
    
    # Quick predictions
    st.subheader("🔮 Prediksi Cepat")
    
    # Use latest data point for prediction
    latest_data = df.iloc[-1]
    
    sample_input = {
        'date': datetime.now().strftime("%Y-%m-%d"),
        'temperature': float(latest_data['temperature']),
        'rainfall': float(latest_data['rainfall']),
        'humidity': float(latest_data['humidity']),
        'holiday': int(latest_data['holiday']),
        'weekend': int(latest_data['weekend']),
        'population_density': float(latest_data['population_density']),
        'event_level': int(latest_data['event_level'])
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        daily_pred = predictor.predict_daily(sample_input)
        st.metric("Prediksi Hari Ini", f"{daily_pred:.2f} ton", delta=f"{daily_pred - avg_waste:.2f}")
    
    with col2:
        weekly_pred = predictor.predict_weekly(sample_input)
        st.metric("Prediksi Mingguan", f"{weekly_pred['total_volume']:.2f} ton")
    
    with col3:
        monthly_pred = predictor.predict_monthly(sample_input)
        st.metric("Prediksi Bulanan", f"{monthly_pred['total_volume']:.2f} ton")
    
    # Fleet recommendation
    fleet = predictor.calculate_fleet_recommendation(daily_pred)
    st.info(f"🚛 **Rekomendasi Armada Hari Ini**: {fleet['trucks_needed']} truk (kapasitas {fleet['truck_capacity']} ton/truk, utilisasi {fleet['utilization_rate']}%)")
    
    st.markdown("---")
    
    # Trend visualization
    st.subheader("📈 Tren Volume Sampah")
    
    # Last 90 days
    df_recent = df.tail(90).copy()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_recent['date'],
        y=df_recent['waste_volume'],
        mode='lines',
        name='Volume Sampah',
        line=dict(color='steelblue', width=2)
    ))
    
    fig.update_layout(
        title="Volume Sampah 90 Hari Terakhir",
        xaxis_title="Tanggal",
        yaxis_title="Volume Sampah (ton)",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def page_data_analysis():
    """Data Analysis Page"""
    st.markdown('<div class="main-header">📊 Analisis Data</div>', unsafe_allow_html=True)
    
    df = load_dataset()
    
    if df is None:
        st.error("❌ Dataset tidak ditemukan. Jalankan `python src/train_model.py` terlebih dahulu.")
        return
    
    # Dataset preview
    st.subheader("🔍 Preview Dataset")
    st.dataframe(df.head(20), use_container_width=True)
    
    # Descriptive statistics
    st.subheader("📈 Statistik Deskriptif")
    st.dataframe(df.describe(), use_container_width=True)
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📉 Distribusi Volume Sampah")
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(df['waste_volume'], bins=50, color='steelblue', edgecolor='black', alpha=0.7)
        ax.set_xlabel('Volume Sampah (ton)', fontweight='bold')
        ax.set_ylabel('Frekuensi', fontweight='bold')
        ax.set_title('Distribusi Volume Sampah', fontweight='bold')
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    
    with col2:
        st.subheader("📊 Volume Berdasarkan Hari")
        day_names = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
        df['day_name'] = df['date'].dt.dayofweek.map(lambda x: day_names[x])
        daily_avg = df.groupby('day_name')['waste_volume'].mean().reindex(day_names)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        daily_avg.plot(kind='bar', ax=ax, color='darkgreen', edgecolor='black')
        ax.set_xlabel('Hari', fontweight='bold')
        ax.set_ylabel('Rata-rata Volume (ton)', fontweight='bold')
        ax.set_title('Rata-rata Volume Sampah per Hari', fontweight='bold')
        ax.set_xticklabels(day_names, rotation=45)
        ax.grid(True, alpha=0.3, axis='y')
        st.pyplot(fig)
    
    st.markdown("---")
    
    # Monthly trends
    st.subheader("📅 Tren Bulanan")
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    monthly_avg = df.groupby('year_month')['waste_volume'].mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_avg.index,
        y=monthly_avg.values,
        mode='lines+markers',
        name='Rata-rata Bulanan',
        line=dict(color='coral', width=3),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title="Rata-rata Volume Sampah Bulanan",
        xaxis_title="Bulan",
        yaxis_title="Volume Sampah (ton)",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Correlation heatmap
    st.subheader("🔥 Korelasi Antar Variabel")
    
    correlation_cols = ['temperature', 'rainfall', 'humidity', 'holiday', 
                       'weekend', 'population_density', 'event_level', 'waste_volume']
    corr_matrix = df[correlation_cols].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, square=True, ax=ax, cbar_kws={'label': 'Korelasi'})
    ax.set_title('Heatmap Korelasi', fontweight='bold', fontsize=14)
    st.pyplot(fig)


def page_prediction():
    """Prediction Page"""
    st.markdown('<div class="main-header">🔮 Prediksi Volume Sampah</div>', unsafe_allow_html=True)
    
    predictor = load_predictor()
    
    if predictor is None:
        st.error("❌ Model belum tersedia. Jalankan `python src/train_model.py` untuk melatih model terlebih dahulu.")
        st.code("python src/train_model.py", language="bash")
        return
    
    st.success("✅ Model siap digunakan!")
    
    st.markdown("---")
    
    # Input form
    st.subheader("📝 Input Parameter Prediksi")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        input_date = st.date_input(
            "Tanggal",
            value=datetime.now(),
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2030, 12, 31)
        )
        
        temperature = st.slider(
            "Suhu (°C)",
            min_value=24.0,
            max_value=35.0,
            value=29.5,
            step=0.5
        )
        
        rainfall = st.slider(
            "Curah Hujan (mm)",
            min_value=0.0,
            max_value=120.0,
            value=10.0,
            step=1.0
        )
    
    with col2:
        humidity = st.slider(
            "Kelembaban (%)",
            min_value=55.0,
            max_value=95.0,
            value=75.0,
            step=1.0
        )
        
        holiday = st.selectbox(
            "Hari Libur",
            options=[0, 1],
            format_func=lambda x: "Ya" if x == 1 else "Tidak"
        )
        
        weekend = st.selectbox(
            "Akhir Pekan",
            options=[0, 1],
            format_func=lambda x: "Ya" if x == 1 else "Tidak"
        )
    
    with col3:
        population_density = st.number_input(
            "Kepadatan Penduduk (jiwa/km²)",
            min_value=3000,
            max_value=15000,
            value=9000,
            step=100
        )
        
        event_level = st.slider(
            "Tingkat Event (0-5)",
            min_value=0,
            max_value=5,
            value=1,
            step=1
        )
    
    st.markdown("---")
    
    # Prediction button
    if st.button("🚀 Prediksi Sekarang", type="primary", use_container_width=True):
        # Prepare input
        input_data = {
            'date': input_date.strftime("%Y-%m-%d"),
            'temperature': float(temperature),
            'rainfall': float(rainfall),
            'humidity': float(humidity),
            'holiday': int(holiday),
            'weekend': int(weekend),
            'population_density': float(population_density),
            'event_level': int(event_level)
        }
        
        # Make predictions
        with st.spinner("Sedang melakukan prediksi..."):
            daily_details = predictor.predict_daily_with_details(input_data)
            daily_pred = daily_details['predicted_waste_volume']
            weekly_pred = predictor.predict_weekly(input_data)
            monthly_pred = predictor.predict_monthly(input_data)
        
        st.success("✅ Prediksi berhasil!")
        
        st.markdown("---")
        
        # Display results
        st.subheader("📊 Hasil Prediksi")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Prediksi Harian", f"{daily_pred:.2f} ton")
            interval = daily_details['confidence_interval']
            st.caption(f"95% CI: {interval['lower_bound']:.2f} - {interval['upper_bound']:.2f} ton")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Prediksi Mingguan (7 hari)", f"{weekly_pred['total_volume']:.2f} ton")
            st.caption(f"Rata-rata: {weekly_pred['average_daily']:.2f} ton/hari")
            interval = weekly_pred['confidence_interval']
            st.caption(f"95% CI total: {interval['lower_bound']:.2f} - {interval['upper_bound']:.2f} ton")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Prediksi Bulanan (30 hari)", f"{monthly_pred['total_volume']:.2f} ton")
            st.caption(f"Rata-rata: {monthly_pred['average_daily']:.2f} ton/hari")
            interval = monthly_pred['confidence_interval']
            st.caption(f"95% CI total: {interval['lower_bound']:.2f} - {interval['upper_bound']:.2f} ton")
            st.markdown('</div>', unsafe_allow_html=True)

        if daily_details['anomaly']['is_anomaly']:
            st.warning(f"Input terdeteksi anomali: {daily_details['anomaly']['message']}")
        else:
            st.info(f"Status anomali: {daily_details['anomaly']['message']}")
        
        st.markdown("---")
        
        # Fleet recommendation
        st.subheader("🚛 Rekomendasi Armada")
        
        fleet = predictor.calculate_fleet_recommendation(daily_pred)
        
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown(f"""
        **Rekomendasi untuk tanggal {input_date.strftime('%d %B %Y')}:**
        
        - **Jumlah Truk Diperlukan**: {fleet['trucks_needed']} unit
        - **Kapasitas per Truk**: {fleet['truck_capacity']} ton
        - **Total Kapasitas Armada**: {fleet['total_capacity']} ton
        - **Tingkat Utilisasi**: {fleet['utilization_rate']}%
        
        💡 Satu truk dapat mengangkut 8 ton sampah. Dengan prediksi volume {daily_pred:.2f} ton, 
        dibutuhkan {fleet['trucks_needed']} truk untuk mengangkut seluruh sampah.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Weekly breakdown
        st.subheader("📅 Rincian Prediksi Mingguan")
        
        weekly_df = pd.DataFrame(weekly_pred['daily_predictions'])
        weekly_df['date'] = pd.to_datetime(weekly_df['date'])
        weekly_df['day_name'] = weekly_df['day_name'].str[:3]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=weekly_df['day_name'] + '<br>' + weekly_df['date'].dt.strftime('%d/%m'),
            y=weekly_df['predicted_volume'],
            marker_color='steelblue',
            text=weekly_df['predicted_volume'].round(2),
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Prediksi Volume Sampah 7 Hari Ke Depan",
            xaxis_title="Hari",
            yaxis_title="Volume (ton)",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("Export Prediksi")

        weekly_summary = {
            "prediction_type": "weekly",
            "start_date": input_data['date'],
            "end_date": weekly_pred['daily_predictions'][-1]['date'],
            "total_volume": weekly_pred['total_volume'],
            "average_daily": weekly_pred['average_daily'],
        }
        monthly_summary = {
            "prediction_type": "monthly",
            "start_date": input_data['date'],
            "end_date": monthly_pred['daily_predictions'][-1]['date'],
            "total_volume": monthly_pred['total_volume'],
            "average_daily": monthly_pred['average_daily'],
        }

        export_col1, export_col2, export_col3, export_col4 = st.columns(4)
        with export_col1:
            st.download_button(
                "Weekly Excel",
                export_predictions_to_excel(weekly_summary, weekly_pred['daily_predictions']),
                file_name="weekly_waste_prediction.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with export_col2:
            st.download_button(
                "Weekly PDF",
                export_predictions_to_pdf(weekly_summary, weekly_pred['daily_predictions']),
                file_name="weekly_waste_prediction.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        with export_col3:
            st.download_button(
                "Monthly Excel",
                export_predictions_to_excel(monthly_summary, monthly_pred['daily_predictions']),
                file_name="monthly_waste_prediction.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with export_col4:
            st.download_button(
                "Monthly PDF",
                export_predictions_to_pdf(monthly_summary, monthly_pred['daily_predictions']),
                file_name="monthly_waste_prediction.pdf",
                mime="application/pdf",
                use_container_width=True,
            )


def page_model_performance():
    """Model Performance Page"""
    st.markdown('<div class="main-header">⚡ Performa Model</div>', unsafe_allow_html=True)
    
    project_root = Path(__file__).parent.parent
    report_path = project_root / "reports" / "evaluation_report.md"
    feature_importance_path = project_root / "reports" / "feature_importance.png"
    prediction_comparison_path = project_root / "reports" / "prediction_comparison.png"
    metadata_path = project_root / "models" / "prediction_metadata.pkl"
    
    # Display evaluation report
    if report_path.exists():
        st.subheader("📄 Laporan Evaluasi Model")
        with open(report_path, 'r', encoding='utf-8') as f:
            report = f.read()
        st.markdown(report)
    else:
        st.warning("⚠️ Laporan evaluasi belum tersedia. Jalankan `python src/train_model.py` terlebih dahulu.")
    
    st.markdown("---")
    
    # Display feature importance
    if feature_importance_path.exists():
        st.subheader("🎯 Feature Importance")
        st.image(str(feature_importance_path), use_column_width=True)
    
    # Display prediction comparison
    if prediction_comparison_path.exists():
        st.subheader("📊 Perbandingan Prediksi")
        st.image(str(prediction_comparison_path), use_column_width=True)

    st.markdown("---")
    st.subheader("Phase 2 Model Metadata")
    if metadata_path.exists():
        metadata = joblib.load(metadata_path)
        st.json(metadata)
    else:
        st.warning("Metadata Phase 2 belum tersedia. Jalankan `python src/train_model.py` terlebih dahulu.")


def page_smart_bin_iot():
    """Smart Bin IoT monitoring page."""
    st.markdown('<div class="main-header">Smart Bin IoT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Monitoring level tempat sampah dari ESP32</div>', unsafe_allow_html=True)

    if st.button("Refresh Data", use_container_width=True):
        st.rerun()

    try:
        readings = get_latest_readings(limit=50)
    except Exception as e:
        st.error(f"Gagal membaca database IoT: {e}")
        return

    if not readings:
        st.warning("Belum ada data ESP32. Kirim data ke endpoint `/iot/bin-reading` terlebih dahulu.")
        st.code(
            'curl -X POST http://localhost:8000/iot/bin-reading '
            '-H "Content-Type: application/json" '
            '-d "{\\"bin_id\\":\\"TPS-001\\",\\"fill_level\\":72.5,\\"device_id\\":\\"ESP32-001\\"}"',
            language="bash",
        )
        return

    df = pd.DataFrame(readings)
    df["created_at"] = pd.to_datetime(df["created_at"])
    latest = df.iloc[0]

    status_colors = {
        "low": "#28a745",
        "medium": "#ffc107",
        "high": "#fd7e14",
        "full": "#dc3545",
    }
    status_color = status_colors.get(latest["status"], "#1f77b4")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Bin Terbaru", latest["bin_id"])
    with col2:
        st.metric("Fill Level", f"{latest['fill_level']:.1f}%")
    with col3:
        st.markdown(
            f"""
            <div style="background-color:{status_color}; color:white; padding:0.8rem; border-radius:0.5rem; text-align:center; font-weight:bold;">
                {latest['status'].upper()}
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.metric("Device", latest["device_id"])

    st.caption(f"Update terakhir: {latest['created_at'].strftime('%Y-%m-%d %H:%M:%S UTC')}")
    st.progress(min(float(latest["fill_level"]) / 100, 1.0))

    st.markdown("---")
    st.subheader("Tren Fill Level")

    chart_df = df.sort_values("created_at")
    fig = px.line(
        chart_df,
        x="created_at",
        y="fill_level",
        color="bin_id",
        markers=True,
        labels={
            "created_at": "Waktu",
            "fill_level": "Fill Level (%)",
            "bin_id": "Bin ID",
        },
    )
    fig.update_layout(height=400, yaxis_range=[0, 100], hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Data Terbaru")
    display_df = df[["created_at", "bin_id", "device_id", "fill_level", "status"]].copy()
    display_df["created_at"] = display_df["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    st.dataframe(display_df, use_container_width=True)


def page_about():
    """About System Page"""
    st.markdown('<div class="main-header">ℹ️ Tentang Sistem</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ## Latar Belakang
    
    Pengelolaan sampah merupakan tantangan besar bagi kota-kota modern. Volume sampah yang fluktuatif 
    seringkali menyebabkan inefisiensi dalam pengangkutan, baik berupa kelebihan atau kekurangan armada. 
    Sistem ini dikembangkan untuk mengatasi masalah tersebut dengan memanfaatkan teknologi Machine Learning.
    
    ## Permasalahan Industri
    
    1. **Ketidakpastian Volume Sampah**: Volume sampah harian sangat bervariasi tergantung berbagai faktor
    2. **Inefisiensi Armada**: Sulit menentukan jumlah truk yang optimal untuk setiap hari
    3. **Biaya Operasional Tinggi**: Penggunaan armada yang tidak optimal meningkatkan biaya
    4. **Dampak Lingkungan**: Sampah yang menumpuk berdampak negatif pada lingkungan
    
    ## Solusi AI
    
    Sistem ini menggunakan algoritma **Random Forest** dan **XGBoost** untuk memprediksi volume sampah 
    berdasarkan:
    
    - 🌡️ Kondisi cuaca (suhu, curah hujan, kelembaban)
    - 📅 Kalender (hari kerja, akhir pekan, hari libur)
    - 👥 Kepadatan penduduk
    - 🎉 Tingkat event/kegiatan khusus
    
    Model dipilih berdasarkan performa terbaik pada metrik RMSE, MAE, R², dan MAPE.
    
    ## Manfaat Sistem
    
    ✅ **Efisiensi Operasional**: Optimasi jumlah armada berdasarkan prediksi akurat  
    ✅ **Penghematan Biaya**: Mengurangi biaya operasional hingga 20-30%  
    ✅ **Perencanaan Strategis**: Data untuk perencanaan jangka panjang  
    ✅ **Lingkungan Bersih**: Pengangkutan tepat waktu mencegah penumpukan sampah  
    
    ## Target Pengguna
    
    - 🏛️ Dinas Lingkungan Hidup Kota
    - 🌆 Tim Smart City
    - 🚛 Perusahaan Pengelola Sampah
    - 📊 Tim Perencanaan Kota
    
    ## Teknologi yang Digunakan
    
    | Komponen | Teknologi |
    |----------|-----------|
    | Backend ML | Python 3.11, Scikit-Learn, XGBoost |
    | Data Processing | Pandas, NumPy |
    | Visualization | Matplotlib, Seaborn, Plotly |
    | Dashboard | Streamlit |
    | API | FastAPI, Uvicorn |
    | Model Persistence | Joblib |
    
    ## Metrik Performa
    
    Model dievaluasi menggunakan:
    
    - **MAE** (Mean Absolute Error): Rata-rata kesalahan absolut
    - **RMSE** (Root Mean Squared Error): Akar kuadrat rata-rata kesalahan kuadrat
    - **R²** (R-squared): Proporsi varians yang dijelaskan model
    - **MAPE** (Mean Absolute Percentage Error): Rata-rata kesalahan persentase
    
    ## Batasan Sistem
    
    - Prediksi didasarkan pada pola historis dan mungkin tidak akurat untuk kondisi ekstrem
    - Memerlukan data historis minimal 1 tahun untuk performa optimal
    - Perlu retraining berkala dengan data terbaru
    
    ## Pengembangan Lanjutan
    
    🔮 **Future Enhancements**:
    - Integrasi dengan IoT sensors di TPS (Tempat Pembuangan Sementara)
    - Real-time tracking armada
    - Optimasi rute pengangkutan
    - Prediksi jenis sampah (organik, anorganik, B3)
    - Mobile application untuk petugas lapangan
    
    ---
    
    **Dikembangkan dengan ❤️ menggunakan Python & Machine Learning**
    
    © 2024 Waste Volume Prediction System
    """)


def main():
    """Main application"""
    
    # Sidebar
    st.sidebar.title("🗂️ Menu Navigasi")
    
    page = st.sidebar.radio(
        "Pilih Halaman:",
        [
            "🏠 Dashboard Utama",
            "📊 Analisis Data",
            "🔮 Prediksi Volume Sampah",
            "Smart Bin IoT",
            "⚡ Performa Model",
            "ℹ️ Tentang Sistem"
        ]
    )
    
    st.sidebar.markdown("---")
    
    # System info
    st.sidebar.subheader("ℹ️ Informasi Sistem")
    st.sidebar.info("""
    **Sistem Prediksi Volume Sampah**
    
    Menggunakan Machine Learning untuk 
    memprediksi volume sampah harian, 
    mingguan, dan bulanan.
    
    **Algoritma**: Random Forest & XGBoost
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2024 Waste Volume Prediction System")
    
    # Route to pages
    if "Dashboard Utama" in page:
        page_dashboard()
    elif "Analisis Data" in page:
        page_data_analysis()
    elif "Prediksi Volume Sampah" in page:
        page_prediction()
    elif "Smart Bin IoT" in page:
        page_smart_bin_iot()
    elif "Performa Model" in page:
        page_model_performance()
    elif "Tentang Sistem" in page:
        page_about()


if __name__ == "__main__":
    main()
