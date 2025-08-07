import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Konfigurasi halaman
st.set_page_config(
    page_title="Dasbor Bencana Kebakaran Jakarta",
    page_icon="🔥",
    layout="wide",
)

# Menambahkan CSS kustom
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF5733;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #343a40;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .insights-text {
        background-color: #f8f9fa;
        color: #343a40;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #FF5733;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        box-shadow: 0 0.15rem 0.3rem rgba(0, 0, 0, 0.15);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #FF5733;
    }
    .metric-label {
        font-size: 1rem;
        color: #6c757d;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #6c757d;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Persiapan data
@st.cache_data
def load_data():
    # Membaca data
    # Pastikan file CSV 'Data_Kebakaran_Gabungan (1).csv' ada di direktori yang sama
    df = pd.read_csv('Data_Kebakaran_Gabungan (1).csv', sep=';')
    
    # Mengubah nama kolom agar lebih mudah digunakan
    df.columns = ['periode_data', 'wilayah', 'kecamatan', 'kelurahan', 'frekuensi', 
                'gas', 'lainnya', 'lilin', 'listrik', 'membakar_sampah', 'rokok']
    
    # Menghitung total insiden berdasarkan penyebab
    df['total_by_cause'] = df['gas'] + df['lainnya'] + df['lilin'] + df['listrik'] + df['membakar_sampah'] + df['rokok']
    
    # Membuat klasifikasi wilayah Jakarta
    df['region_short'] = df['wilayah'].apply(lambda x: x.split()[-1].replace('.', ''))
    
    return df

df = load_data()

# Header utama
st.markdown("<h1 class='main-header'>Dasbor Insiden Kebakaran Jakarta (2024)</h1>", unsafe_allow_html=True)

# Baris metrik kunci
st.markdown("<h2 class='sub-header'>Statistik Utama</h2>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("<div class='metric-container'><div class='metric-value'>{}</div><div class='metric-label'>Total Kebakaran</div></div>".format(
        df['frekuensi'].sum()), unsafe_allow_html=True)

with col2:
    st.markdown("<div class='metric-container'><div class='metric-value'>{}</div><div class='metric-label'>Lokasi Terdampak</div></div>".format(
        len(df)), unsafe_allow_html=True)
        
with col3:
    st.markdown("<div class='metric-container'><div class='metric-value'>{:.1f}%</div><div class='metric-label'>Kebakaran Akibat Listrik</div></div>".format(
        df['listrik'].sum() / df['total_by_cause'].sum() * 100), unsafe_allow_html=True)

with col4:
    highest_kelurahan = df.sort_values('frekuensi', ascending=False).iloc[0]['kelurahan']
    st.markdown("<div class='metric-container'><div class='metric-value'>{}</div><div class='metric-label'>Area Risiko Tertinggi</div></div>".format(
        highest_kelurahan), unsafe_allow_html=True)
        
with col5:
    avg_incidents = df['frekuensi'].mean()
    st.markdown("<div class='metric-container'><div class='metric-value'>{:.1f}</div><div class='metric-label'>Rata-rata Kebakaran per Area</div></div>".format(
        avg_incidents), unsafe_allow_html=True)

# Filter di sidebar
st.sidebar.title("Filter")

# Filter Wilayah
regions = sorted(df['wilayah'].unique())
selected_regions = st.sidebar.multiselect("Pilih Wilayah", regions, default=regions)

# Filter Kecamatan (tergantung wilayah)
filtered_df = df[df['wilayah'].isin(selected_regions)]
districts = sorted(filtered_df['kecamatan'].unique())
selected_districts = st.sidebar.multiselect("Pilih Kecamatan", districts, default=[])

# Filter Kelurahan (tergantung kecamatan)
if selected_districts:
    filtered_df = filtered_df[filtered_df['kecamatan'].isin(selected_districts)]
    
sub_districts = sorted(filtered_df['kelurahan'].unique())
selected_sub_districts = st.sidebar.multiselect("Pilih Kelurahan", sub_districts, default=[])

# Pemfilteran akhir
if selected_sub_districts:
    filtered_df = filtered_df[filtered_df['kelurahan'].isin(selected_sub_districts)]
elif selected_districts:
    filtered_df = df[df['kecamatan'].isin(selected_districts)]
else:
    filtered_df = df[df['wilayah'].isin(selected_regions)]

# Tabulasi visualisasi
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Persebaran Kebakaran", "Analisis Penyebab", "Area Risiko Tinggi", "Wawasan", "Peta Persebaran"])

with tab1:
    st.markdown("<h2 class='sub-header'>Persebaran Bencana Kebakaran</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribusi berdasarkan wilayah
        region_data = filtered_df.groupby('wilayah')['frekuensi'].sum().reset_index()
        fig = px.bar(region_data, 
                     x='wilayah', 
                     y='frekuensi', 
                     title='Bencana Kebakaran Berdasarkan Wilayah',
                     color='frekuensi',
                     color_continuous_scale='Reds',
                     labels={'wilayah': 'Wilayah', 'frekuensi': 'Frekuensi'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribusi berdasarkan kecamatan (15 teratas)
        district_data = filtered_df.groupby('kecamatan')['frekuensi'].sum().sort_values(ascending=False).head(15).reset_index()
        fig = px.bar(district_data, 
                     x='frekuensi', 
                     y='kecamatan', 
                     title='Kecamatan dengan Frekuensi Kebakaran Tertinggi',
                     color='frekuensi',
                     color_continuous_scale='Reds',
                     labels={'kecamatan': 'Kecamatan', 'frekuensi': 'Frekuensi'},
                     orientation='h')
        fig.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Treemap insiden berdasarkan Wilayah > Kecamatan > Kelurahan
    st.markdown("<h3>Distribusi Hirarkis Insiden Kebakaran</h3>", unsafe_allow_html=True)
    fig = px.treemap(filtered_df, 
                     path=['wilayah', 'kecamatan', 'kelurahan'], 
                     values='frekuensi',
                     color='frekuensi',
                     color_continuous_scale='Reds',
                     title='Tampilan Hirarkis Insiden Kebakaran')
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("<h2 class='sub-header'>Analisis Penyebab Kebakaran</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Diagram pai untuk penyebab
        causes = ['gas', 'lainnya', 'lilin', 'listrik', 'membakar_sampah', 'rokok']
        cause_names = ['Gas', 'Lainnya', 'Lilin', 'Listrik', 'Membakar Sampah', 'Rokok']
        cause_data = filtered_df[causes].sum()
        
        fig = px.pie(values=cause_data.values, 
                     names=cause_names, 
                     title='Distribusi Penyebab Kebakaran',
                     color_discrete_sequence=px.colors.sequential.Reds)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Perbandingan penyebab antar wilayah
        cause_by_region = filtered_df.groupby('region_short')[causes].sum().reset_index()
        cause_by_region_melted = pd.melt(cause_by_region, 
                                          id_vars=['region_short'], 
                                          value_vars=causes,
                                          var_name='cause', value_name='count')
        
        # Memetakan kode penyebab ke nama yang mudah dibaca
        cause_mapping = dict(zip(causes, cause_names))
        cause_by_region_melted['cause'] = cause_by_region_melted['cause'].map(cause_mapping)
        
        fig = px.bar(cause_by_region_melted, 
                     x='region_short', 
                     y='count', 
                     color='cause',
                     title='Penyebab Kebakaran Berdasarkan Wilayah',
                     labels={'region_short': 'Wilayah Jakarta', 'count': 'Jumlah Insiden', 'cause': 'Penyebab'},
                     color_discrete_sequence=px.colors.sequential.Reds_r)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Analisis penyebab mendetail - Diagram garis untuk kecamatan teratas
    top_districts = filtered_df.groupby('kecamatan')['frekuensi'].sum().sort_values(ascending=False).head(10).index
    top_district_data = filtered_df[filtered_df['kecamatan'].isin(top_districts)].groupby('kecamatan')[causes].sum().reset_index()
    
    top_district_data_melted = pd.melt(top_district_data, 
                                        id_vars=['kecamatan'], 
                                        value_vars=causes,
                                        var_name='cause', value_name='count')
    top_district_data_melted['cause'] = top_district_data_melted['cause'].map(cause_mapping)
    
    fig = px.line(top_district_data_melted, 
                 x='kecamatan', 
                 y='count', 
                 color='cause',
                 title='Penyebab Kebakaran di 10 Kecamatan Teratas',
                 labels={'kecamatan': 'Kecamatan', 'count': 'Jumlah Insiden', 'cause': 'Penyebab'},
                 markers=True,
                 line_shape="spline",
                 color_discrete_sequence=px.colors.sequential.Reds_r)
    fig.update_layout(height=500, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("<h2 class='sub-header'>Analisis Area Berisiko Tinggi</h2>", unsafe_allow_html=True)
    
    # 15 kelurahan teratas berdasarkan insiden kebakaran
    top_subdistricts = filtered_df.sort_values('frekuensi', ascending=False).head(15)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(top_subdistricts, 
                     x='frekuensi', 
                     y='kelurahan', 
                     title='15 Kelurahan Berisiko Paling Tinggi',
                     color='frekuensi',
                     color_continuous_scale='Reds',
                     orientation='h',
                     labels={'kelurahan': 'Kelurahan', 'frekuensi': 'Jumlah Insiden'})
        fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Rincian penyebab untuk kelurahan berisiko tertinggi
        highest_risk = top_subdistricts.iloc[0]['kelurahan']
        highest_risk_data = filtered_df[filtered_df['kelurahan'] == highest_risk][causes].iloc[0]
        
        fig = px.bar(x=cause_names, 
                     y=highest_risk_data.values, 
                     title=f'Rincian Penyebab untuk {highest_risk}',
                     color=cause_names,
                     color_discrete_sequence=px.colors.sequential.Reds_r,
                     labels={'x': 'Penyebab', 'y': 'Jumlah Insiden'})
        fig.update_layout(height=500, xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap korelasi antara penyebab dan frekuensi
    st.markdown("<h3>Korelasi Antara Penyebab dan Frekuensi Total</h3>", unsafe_allow_html=True)
    
    corr_columns = ['frekuensi'] + causes
    corr_df = filtered_df[corr_columns].corr()
    
    fig = px.imshow(corr_df, 
                    text_auto=True, 
                    color_continuous_scale='Reds',
                    title='Korelasi Antara Berbagai Penyebab dan Frekuensi Total')
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("<h2 class='sub-header'>Wawasan Utama</h2>", unsafe_allow_html=True)
    
    # Membuat metrik untuk wawasan
    col1, col2 = st.columns(2)
    
    with col1:
        listrik_pct = df['listrik'].sum() / df['total_by_cause'].sum() * 100
        st.markdown(f"""
        <div class='insights-text'>
        <h3>Masalah Listrik - Bahaya Kebakaran Utama</h3>
        <p>Masalah kelistrikan adalah penyebab dominan kebakaran di Jakarta, mencakup <b>{listrik_pct:.1f}%</b> dari semua insiden. 
        Hal ini menunjukkan kebutuhan mendesak untuk kesadaran keselamatan listrik dan perbaikan infrastruktur di seluruh kota.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Menghitung kecamatan dengan kebakaran terkait listrik tertinggi
        district_electrical = df.groupby('kecamatan')['listrik'].sum().sort_values(ascending=False)
        highest_electrical_district = district_electrical.index[0]
        highest_electrical_count = district_electrical.iloc[0]
        
        st.markdown(f"""
        <div class='insights-text'>
        <h3>Area Listrik Berisiko Tinggi</h3>
        <p>Kecamatan <b>{highest_electrical_district}</b> memiliki jumlah kebakaran akibat listrik tertinggi ({highest_electrical_count}), 
        menunjukkan bahwa area ini mungkin memerlukan intervensi keselamatan listrik yang ditargetkan atau peningkatan infrastruktur.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Mencari area dengan insiden pembakaran sampah tertinggi
        trash_district = df.groupby('kecamatan')['membakar_sampah'].sum().sort_values(ascending=False)
        highest_trash_district = trash_district.index[0]
        highest_trash_count = trash_district.iloc[0]
        
        st.markdown(f"""
        <div class='insights-text'>
        <h3>Hubungan dengan Pengelolaan Sampah</h3>
        <p>Kecamatan <b>{highest_trash_district}</b> memiliki jumlah kebakaran tertinggi yang disebabkan oleh pembakaran sampah ({highest_trash_count}). 
        Hal ini menyoroti potensi hubungan antara praktik pengelolaan sampah dan insiden kebakaran di area tertentu.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Perbandingan wilayah
        region_freq = df.groupby('region_short')['frekuensi'].sum().sort_values(ascending=False)
        highest_region = region_freq.index[0]
        lowest_region = region_freq.index[-1]
        
        st.markdown(f"""
        <div class='insights-text'>
        <h3>Kesenjangan Regional</h3>
        <p>Jakarta <b>{highest_region}</b> memiliki jumlah insiden kebakaran tertinggi, sedangkan Jakarta <b>{lowest_region}</b> memiliki yang terendah.
        Kesenjangan geografis ini mungkin terkait dengan perbedaan kepadatan bangunan, penegakan peraturan bangunan, atau kemampuan tanggap darurat.</p>
        </div>
        """, unsafe_allow_html=True)

with tab5:
    with st.container():
        st.markdown("<style>iframe {width: 100%; background-color: white;}</style><h2 class='sub-header'>Peta</h2>", unsafe_allow_html=True)
        st.components.v1.iframe(src="https://datawrapper.dwcdn.net/oSBOq/1/", height=500, scrolling=True)

# Menambahkan footer
st.markdown("<div class='footer'>© 2025 Analisis Keselamatan Kebakaran Jakarta | Sumber data: Dinas Pemadam Kebakaran Jakarta</div>", unsafe_allow_html=True)