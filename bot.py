import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go  # <-- Add this for layout updates
from io import BytesIO
from fpdf import FPDF
import base64
import smtplib
from email.message import EmailMessage
from streamlit_extras.stylable_container import stylable_container
import urllib.parse
# Temporarily comment out pycaret imports while installing
# from pycaret.classification import setup as cls_setup, compare_models as cls_compare, pull as cls_pull
# from pycaret.clustering import setup as clu_setup, create_model as clu_create, assign_model

# --- Custom Plotly Colors and Layout (moved here for global access) ---
custom_colors = [
    '#FF6B6B', '#FFD93D', '#6BCB77', '#4D96FF', '#845EC2', '#FFC75F', '#F9F871', '#00C9A7', '#F76E11', '#F9F871',
    '#FF9671', '#0081CF', '#B8DE6F', '#D65DB1', '#FF61A6', '#3EC300', '#F7B801', '#EA7317', '#A3A847', '#F9A1BC'
]
custom_plotly_layout = dict(
    paper_bgcolor='#181A20',
    plot_bgcolor='linear-gradient(135deg, #23272f 0%, #181A20 100%)',
    font=dict(family='Inter, sans-serif', color='#fff', size=16),
    xaxis=dict(gridcolor='#333', zerolinecolor='#555', linecolor='#888', tickfont=dict(color='#fff')),
    yaxis=dict(gridcolor='#333', zerolinecolor='#555', linecolor='#888', tickfont=dict(color='#fff')),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#fff', size=14)),
    margin=dict(l=40, r=40, t=60, b=40),
)

# --- Custom Plotly Color Themes ---
PLOTLY_THEMES = {
    "Vibrant": {
        "bg": "#181A20",
        "colors": ['#FF6B6B', '#FFD93D', '#6BCB77', '#4D96FF', '#845EC2', '#FFC75F', '#F9F871', '#00C9A7', '#F76E11', '#FF9671']
    },
    "Cool Blues": {
        "bg": "#23272f",
        "colors": ['#4D96FF', '#00C9A7', '#0081CF', '#6BCB77', '#B8DE6F', '#23272f', '#181A20', '#FFC75F', '#FFD93D', '#F9F871']
    },
    "Sunset": {
        "bg": "#2d132c",
        "colors": ['#F76E11', '#FF6B6B', '#FFD93D', '#FF9671', '#845EC2', '#D65DB1', '#FF61A6', '#F9A1BC', '#F7B801', '#EA7317']
    },
    "Minty": {
        "bg": "#1b2e2e",
        "colors": ['#6BCB77', '#00C9A7', '#B8DE6F', '#3EC300', '#A3A847', '#0081CF', '#4D96FF', '#FFC75F', '#FFD93D', '#F9F871']
    },
    "Classic": {
        "bg": "#222",
        "colors": px.colors.qualitative.Plotly
    }
}

# Custom CSS for modern styling and animations
st.markdown("""
<style>
    /* Modern CSS with animations and hover effects */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 0;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        animation: slideInDown 0.8s ease-out;
    }
    
    @keyframes slideInDown {
        from {
            transform: translateY(-50px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .header-title {
        color: white;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from {
            text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 15px #667eea;
        }
        to {
            text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #667eea;
        }
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        border-right: 2px solid #dee2e6;
    }
    
    /* Upload button styling */
    .upload-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .upload-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    }
    
    @keyframes fadeInUp {
        from {
            transform: translateY(30px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white !important;
        color: #222 !important;
        border-radius: 10px 10px 0 0;
        border: none;
        padding: 12px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab"]:hover,
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #fff !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    /* Card styling */
    .card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-left: 4px solid #667eea;
        animation: slideInRight 0.6s ease-out;
    }
    
    .card:hover {
        transform: translateX(5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        border-left-color: #764ba2;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(30px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .stRadio > div:hover {
        box-shadow: 0 5px 15px rgba(0,0,0,0.15);
    }
    
    /* Success message styling */
    .success-message {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        animation: bounceIn 0.6s ease-out;
    }
    
    @keyframes bounceIn {
        0% {
            transform: scale(0.3);
            opacity: 0;
        }
        50% {
            transform: scale(1.05);
        }
        70% {
            transform: scale(0.9);
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    /* Warning message styling */
    .warning-message {
        background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.7);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(255, 193, 7, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(255, 193, 7, 0);
        }
    }
    
    /* Info message styling */
    .info-message {
        background: linear-gradient(135deg, #17a2b8 0%, #6f42c1 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        animation: fadeIn 0.8s ease-out;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    /* Dataframe styling */
    .dataframe-container {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        animation: zoomIn 0.6s ease-out;
    }
    
    @keyframes zoomIn {
        from {
            transform: scale(0.9);
            opacity: 0;
        }
        to {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    /* Loading animation */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255,255,255,.3);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2rem;
        }
        .card {
            padding: 1rem;
        }
    }
    /* Fix radio button group background and label text */
    .stRadio > div {
        background: #23272f !important;
        color: #fff !important;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    }
    .stRadio label {
        color: #fff !important;
        font-weight: 500;
    }
    .stRadio input[type="radio"]:checked + div,
    .stRadio label:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #fff !important;
        border-radius: 8px;
        transition: background 0.2s;
    }
    /* Selectbox, Multiselect, Text input, etc. */
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stTextInput > div > input,
    .stTextArea > div > textarea {
        background: #23272f !important;
        color: #fff !important;
        border-radius: 10px;
        border: 2px solid #444;
        transition: border 0.2s;
    }
    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within,
    .stTextInput > div > input:focus,
    .stTextArea > div > textarea:focus {
        border: 2px solid #764ba2 !important;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Smart CSV Analyzer", layout="wide")

# Header with animation
st.markdown("""
<style>
.custom-header {
    background: #23272f;
    border-radius: 18px;
    box-shadow: 0 4px 24px rgba(102, 126, 234, 0.10);
    padding: 2rem 1.5rem 1.2rem 1.5rem;
    margin-bottom: 2rem;
    text-align: center;
}
.custom-header h1 {
    color: #fff;
    font-size: 2.7rem;
    font-weight: 700;
    margin: 0 0 0.5rem 0;
    letter-spacing: -1px;
    font-family: 'Inter', sans-serif;
}
.custom-header .subtitle {
    color: #bdbdbd;
    font-size: 1.15rem;
    margin: 0;
    font-weight: 400;
    font-family: 'Inter', sans-serif;
}
</style>
<div class="custom-header">
  <h1>🚀 Smart CSV Visualizer</h1>
  <p class="subtitle">Analyze, visualize, and gain insights from your CSV data in seconds.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with upload
with st.sidebar:
    st.markdown("""
    <div class="upload-container">
        <h3 style="color: #667eea; margin-bottom: 1rem;">📁 Upload Your Data</h3>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.markdown("""
        <div class="success-message">
            ✅ File loaded successfully!
        </div>
        """, unsafe_allow_html=True)
        
        # Check if dataframe is empty
        if df.empty:
            st.markdown("""
            <div class="warning-message">
                ⚠️ The uploaded file is empty. Please upload a file with data.
            </div>
            """, unsafe_allow_html=True)
            st.stop()
            
        # Get column information
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        row_count, col_count = df.shape

        # Display basic file info
        st.sidebar.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 5px 15px rgba(0,0,0,0.15); border-left: 4px solid #fff;">
            <h4 style="color: #fff; margin-bottom: 0.5rem;">📊 File Info</h4>
            <p><strong>Rows:</strong> {row_count:,}</p>
            <p><strong>Columns:</strong> {col_count}</p>
            <p><strong>Numeric:</strong> {len(numeric_cols)}</p>
            <p><strong>Categorical:</strong> {len(categorical_cols)}</p>
        </div>
        """, unsafe_allow_html=True)

        tabs = st.tabs(["📊 Data Preview", "🧹 Cleaning", "📈 Visualizations", "💡 Insights", "📤 Export"])

        with tabs[0]:
            st.markdown("""
            <div class="card">
                <h2 style="color: #1f77b4; margin-bottom: 1rem;">📊 Data Preview</h2>
            </div>
            """, unsafe_allow_html=True)
            
            with stylable_container(
                key="scrollable-preview",
                css_styles="overflow:auto; max-height:400px;"
            ):
                st.dataframe(df)
            
            st.markdown("---")
            st.markdown("""
            <div class="card">
                <h3 style="color: #1f77b4; margin-bottom: 1rem;">📋 Data Summary</h3>
            </div>
            """, unsafe_allow_html=True)
            st.write(df.describe())

        with tabs[1]:
            st.markdown("""
            <div class="card">
                <h2 style="color: #2ca02c; margin-bottom: 1rem;">🧹 Data Cleaning</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("**Missing Values**")
            missing_percent = df.isnull().mean() * 100
            missing_data = missing_percent[missing_percent > 0]
            if len(missing_data) > 0:
                st.write(missing_data)
            else:
                st.markdown("""
                <div class="success-message">
                    ✅ No missing values found!
                </div>
                """, unsafe_allow_html=True)

            if len(df.columns) > 0:
                col_to_fix = st.selectbox("Select column to fix", df.columns)
                method = st.radio("Choose fix method", ["Drop rows", "Fill with Mean", "Fill with Median", "Fill with Mode"])

                if st.button("Apply Fix"):
                    try:
                        if method == "Drop rows":
                            df.dropna(subset=[col_to_fix], inplace=True)
                        elif method == "Fill with Mean" and df[col_to_fix].dtype in ['int64', 'float64']:
                            df[col_to_fix].fillna(df[col_to_fix].mean(), inplace=True)
                        elif method == "Fill with Median" and df[col_to_fix].dtype in ['int64', 'float64']:
                            df[col_to_fix].fillna(df[col_to_fix].median(), inplace=True)
                        elif method == "Fill with Mode":
                            mode_value = df[col_to_fix].mode()
                            if len(mode_value) > 0:
                                df[col_to_fix].fillna(mode_value[0], inplace=True)
                        else:
                            st.markdown("""
                            <div class="warning-message">
                                ⚠️ No mode found for this column
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown("""
                        <div class="success-message">
                            ✅ Column cleaned successfully!
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f"""
                        <div class="warning-message">
                            ❌ Error cleaning column: {e}
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("**Duplicate Rows**")
            duplicate_count = df.duplicated().sum()
            if duplicate_count > 0:
                st.write(f"Found {duplicate_count} duplicates")
                if st.button("Remove Duplicates"):
                    df.drop_duplicates(inplace=True)
                    st.markdown("""
                    <div class="success-message">
                        ✅ Duplicates removed!
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="success-message">
                    ✅ No duplicates found
                </div>
                """, unsafe_allow_html=True)

        with tabs[2]:
            st.markdown("""
            <div class="card">
                <h2 style="color: #d62728; margin-bottom: 1rem;">📈 Visualizations</h2>
            </div>
            """, unsafe_allow_html=True)
            
            if len(numeric_cols) > 0:
                theme_name = st.selectbox("Graph Color Theme", list(PLOTLY_THEMES.keys()), index=0)
                theme = PLOTLY_THEMES[theme_name]
                plot_bg = theme["bg"]
                color_seq = theme["colors"]

                graph_type = st.selectbox("Graph Type", ["Line", "Bar", "Scatter", "Box", "Histogram", "Heatmap"])
                x_axis = st.selectbox("X Axis", df.columns)
                y_axis = st.selectbox("Y Axis", numeric_cols)
                group_by = st.selectbox("Group By (Optional)", [None] + df.columns.tolist())

                if st.button("Generate Graph"):
                    try:
                        if graph_type == "Line":
                            fig = px.line(df, x=x_axis, y=y_axis, color=group_by, color_discrete_sequence=color_seq)
                        elif graph_type == "Bar":
                            fig = px.bar(df, x=x_axis, y=y_axis, color=group_by, color_discrete_sequence=color_seq)
                        elif graph_type == "Scatter":
                            fig = px.scatter(df, x=x_axis, y=y_axis, color=group_by, color_discrete_sequence=color_seq)
                        elif graph_type == "Box":
                            fig = px.box(df, x=x_axis, y=y_axis, color=group_by, color_discrete_sequence=color_seq)
                        elif graph_type == "Histogram":
                            fig = px.histogram(df, x=x_axis, y=y_axis, color=group_by, color_discrete_sequence=color_seq)
                        elif graph_type == "Heatmap":
                            if len(numeric_cols) > 1:
                                fig = px.imshow(df[numeric_cols].corr(), color_continuous_scale=color_seq)
                            else:
                                st.markdown("""
                                <div class="warning-message">
                                    ⚠️ Need at least 2 numeric columns for heatmap
                                </div>
                                """, unsafe_allow_html=True)
                                fig = None
                        # Apply custom layout to all figures
                        if fig:
                            fig.update_layout(
                                paper_bgcolor=plot_bg,
                                plot_bgcolor=plot_bg,
                                font=dict(family='Inter, sans-serif', color='#fff', size=16),
                                xaxis=dict(gridcolor='#333', zerolinecolor='#555', linecolor='#888', tickfont=dict(color='#fff')),
                                yaxis=dict(gridcolor='#333', zerolinecolor='#555', linecolor='#888', tickfont=dict(color='#fff')),
                                legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#fff', size=14)),
                                margin=dict(l=40, r=40, t=60, b=40),
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.markdown(f"""
                        <div class="warning-message">
                            ❌ Error generating graph: {e}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="warning-message">
                    ⚠️ No numeric columns found for visualization
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("**Time Series Detection**")
            datetime_cols = []
            
            # First check for existing datetime columns
            existing_datetime_cols = df.select_dtypes(include=["datetime", "datetime64"]).columns.tolist()
            datetime_cols.extend(existing_datetime_cols)
            
            # Try to convert potential datetime columns
            for col in df.columns:
                if col not in datetime_cols:  # Skip if already detected as datetime
                    try:
                        # Create a copy to test conversion without modifying original
                        test_series = pd.to_datetime(df[col], errors='coerce')
                        # Only add if conversion was successful (not all NaT)
                        if test_series.notna().sum() > 0:
                            df[col] = test_series
                            datetime_cols.append(col)
                    except Exception:
                        continue

            if datetime_cols and len(numeric_cols) > 0:
                try:
                    dt_col = st.selectbox("Select datetime column", datetime_cols)
                    if dt_col in df.columns and dt_col in numeric_cols:
                        # Remove datetime column from numeric cols for plotting
                        plot_numeric_cols = [col for col in numeric_cols if col != dt_col]
                        if plot_numeric_cols:
                            st.line_chart(df.set_index(dt_col)[plot_numeric_cols])
                        else:
                            st.markdown("""
                            <div class="info-message">
                                ℹ️ No numeric columns available for time series plotting
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.line_chart(df.set_index(dt_col)[numeric_cols])
                except Exception as e:
                    st.markdown(f"""
                    <div class="warning-message">
                        ❌ Error creating time series chart: {e}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="info-message">
                    ℹ️ No datetime columns detected or no numeric columns for time series
                </div>
                """, unsafe_allow_html=True)

        with tabs[3]:
            st.markdown("""
            <div class="card">
                <h2 style="color: #9467bd; margin-bottom: 1rem;">💡 Insights</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            # --- Carousel Insights ---
            st.markdown("""
            <style>
            .insight-container {
                display: flex;
                overflow-x: auto;
                gap: 12px;
                padding: 10px 0 18px 0;
                scrollbar-width: thin;
                -webkit-overflow-scrolling: touch;
            }
            .insight-card {
                min-width: 180px;
                flex: 0 0 auto;
                background: #23272f;
                color: #fff;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.10);
                padding: 1rem 1rem 0.7rem 1rem;
                border-left: 4px solid #9467bd;
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                transition: transform 0.18s, box-shadow 0.18s;
            }
            .insight-card:hover {
                transform: translateY(-4px) scale(1.03);
                box-shadow: 0 6px 18px rgba(102, 126, 234, 0.18);
                border-left: 4px solid #FFD93D;
            }
            .insight-icon {
                font-size: 1.7rem;
                margin-bottom: 0.5rem;
            }
            .insight-title {
                font-size: 1rem;
                font-weight: 600;
                margin-bottom: 0.2rem;
            }
            .insight-data {
                font-size: 1.2rem;
                font-weight: 700;
                margin-bottom: 0.1rem;
            }
            .insight-desc {
                font-size: 0.95rem;
                color: #bdbdbd;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Generate insights for each categorical column
            value_icon_map = {
                'male': '👨', 'm': '👨', 'female': '👩', 'f': '👩',
                'mobile': '📱', 'desktop': '🖥️', 'tablet': '💊', 'laptop': '💻',
                'credit card': '💳', 'debit card': '🏧', 'paypal': '💸', 'cash': '💵',
                'success': '✅', 'failed': '❌', 'pending': '⏳',
                'q': '🚢', 'c': '⚓', 's': '🛳️',
                'economy': '💺', 'business': '🛫', 'first': '👑',
                'child': '🧒', 'teen': '🧑', 'adult': '🧑‍💼', 'senior': '🧓',
                'yes': '👍', 'no': '👎',
                'true': '✔️', 'false': '❌',
                'cabin': '🛏️', 'ticket': '🎫', 'name': '🧑‍💼', 'class': '🎟️', 'pclass': '🎟️',
                'embarked': '🛳️', 'port': '🛳️', 'city': '🏙️', 'country': '🌍', 'email': '✉️',
                'date': '📅', 'time': '⏰', 'amount': '💰', 'score': '⭐', 'rating': '🌟',
            }
            carousel_html = '<div class="insight-container">'
            for col in categorical_cols:
                vc = df[col].value_counts(dropna=False)
                if len(vc) == 0:
                    continue
                top_val = vc.index[0]
                top_count = vc.iloc[0]
                percent = (top_count / len(df)) * 100
                icon = value_icon_map.get(str(top_val).strip().lower(),
                        value_icon_map.get(col.strip().lower(), '📊'))
                title = f"{col}"
                data = f"{top_val}"
                desc = f"{percent:.1f}% of total ({top_count}/{len(df)})"
                card_html = f'''
                <div class="insight-card">
                    <div class="insight-icon">{icon}</div>
                    <div class="insight-title">{title}</div>
                    <div class="insight-data">{data}</div>
                    <div class="insight-desc">{desc}</div>
                </div>
                '''
                carousel_html += card_html
            carousel_html += '</div>'
            st.markdown(carousel_html, unsafe_allow_html=True)
            st.markdown("---")

            st.markdown("---")
            st.markdown("**Auto Summary**")
            summary = f"The dataset has {row_count} rows and {col_count} columns. The numerical columns are: {', '.join(numeric_cols)}."
            if categorical_cols:
                summary += f" The categorical columns include: {', '.join(categorical_cols)}."
                
                st.markdown(f"""
                <div class="info-message">
                    📋 {summary}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("**AutoML & Feature Importance**")
            st.markdown("""
            <div class="warning-message">
                🚧 ML Analysis feature is temporarily disabled while pycaret is installing. Please wait for the installation to complete.
            </div>
            """, unsafe_allow_html=True)

        with tabs[4]:
            try:
                st.markdown("""
                <div class="card">
                    <h2 style="color: #8c564b; margin-bottom: 1rem;">📤 Export & Share</h2>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                towrite = BytesIO()
                df.to_csv(towrite, index=False)
                towrite.seek(0)
                b64 = base64.b64encode(towrite.read()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="cleaned_data.csv" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 24px; text-decoration: none; border-radius: 10px; display: inline-block; margin: 10px 0; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">📥 Download Cleaned CSV</a>'
                st.markdown(href, unsafe_allow_html=True)

                st.markdown("**Email Report**")
                email_to = st.text_input("Recipient Email")
                email_subject = st.text_input("Email Subject", "CSV Analysis Report")
                email_content = summary

                if st.button("Send Email"):
                    st.markdown("""
                    <div class="warning-message">
                        ⚠️ Email functionality requires proper SMTP configuration. Please update the email settings in the code.
                    </div>
                    """, unsafe_allow_html=True)

                # --- WhatsApp Share Feature ---
                st.markdown("---")
                st.markdown("**Share Insights via WhatsApp**")
                wa_number = st.text_input("Enter WhatsApp number (with country code, e.g. 919876543210)")
                wa_message = f"Hi! Here are the insights from my CSV analysis:\n\n{summary}\n\n(You can also find the attached PDF/report.)"
                encoded_message = urllib.parse.quote(wa_message)
                if wa_number:
                    wa_url = f"https://wa.me/{wa_number}?text={encoded_message}"
                    st.markdown(f'''
                        <a href="{wa_url}" target="_blank" style="background: #25D366; color: white; padding: 12px 24px; border-radius: 10px; text-decoration: none; display: inline-block; margin-top: 10px;">
                            📤 Send Insights on WhatsApp
                        </a>
                        <div style="color: #888; font-size: 0.9em; margin-top: 5px;">
                            <b>Note:</b> You can attach the downloaded CSV or PDF in WhatsApp chat after clicking the button.
                        </div>
                    ''', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div class="warning-message">
                    ❌ Error in Export & WhatsApp section: {e}
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f"""
        <div class="warning-message">
            ❌ Error loading file: {e}
        </div>
        """, unsafe_allow_html=True)

# Add custom CSS for Plotly modebar
st.markdown('''
<style>
    .js-plotly-plot .plotly .modebar {
        background: linear-gradient(135deg, #23272f 0%, #181A20 100%) !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    }
    .js-plotly-plot .plotly .modebar-btn {
        color: #fff !important;
        background: transparent !important;
        border-radius: 6px !important;
        transition: background 0.2s;
    }
    .js-plotly-plot .plotly .modebar-btn:hover {
        background: #764ba2 !important;
        color: #fff !important;
    }
</style>
''', unsafe_allow_html=True)
