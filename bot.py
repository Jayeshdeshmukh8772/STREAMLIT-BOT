import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
from io import BytesIO
from fpdf import FPDF
import base64
import smtplib
from email.message import EmailMessage
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.grid import grid
from pycaret.classification import setup as cls_setup, compare_models as cls_compare, pull as cls_pull
from pycaret.clustering import setup as clu_setup, create_model as clu_create, assign_model

st.set_page_config(page_title="Smart CSV Analyzer", layout="wide")
st.markdown("<h1 style='text-align: center; color: #4A4A4A;'>Smart CSV Visualizer</h1>", unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader("📁 Upload your CSV file", type=["csv"])


if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("File loaded successfully")
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    row_count, col_count = df.shape

    tabs = st.tabs(["Data Preview", "Cleaning", "Visualizations", "Insights", "Export"])

    with tabs[0]:
        st.markdown("<h2 style='color: #1f77b4;'>Data Preview</h2>", unsafe_allow_html=True)
        with stylable_container(
            key="scrollable-preview",
            css_styles="overflow:auto; max-height:400px;"
        ):
            st.dataframe(df)
        st.markdown("---")
        st.markdown("<h3 style='color: #1f77b4;'>Data Summary</h3>", unsafe_allow_html=True)
        st.write(df.describe())

    with tabs[1]:
        st.markdown("<h2 style='color: #2ca02c;'>Data Cleaning</h2>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**Missing Values**")
        missing_percent = df.isnull().mean() * 100
        st.write(missing_percent[missing_percent > 0])

        col_to_fix = st.selectbox("Select column to fix", df.columns)
        method = st.radio("Choose fix method", ["Drop rows", "Fill with Mean", "Fill with Median", "Fill with Mode"])

        if st.button("Apply Fix"):
            if method == "Drop rows":
                df.dropna(subset=[col_to_fix], inplace=True)
            elif method == "Fill with Mean":
                df[col_to_fix].fillna(df[col_to_fix].mean(), inplace=True)
            elif method == "Fill with Median":
                df[col_to_fix].fillna(df[col_to_fix].median(), inplace=True)
            else:
                df[col_to_fix].fillna(df[col_to_fix].mode()[0], inplace=True)
            st.success("Column cleaned")

        st.markdown("---")
        st.markdown("**Duplicate Rows**")
        if df.duplicated().sum() > 0:
            st.write(f"Found {df.duplicated().sum()} duplicates")
            if st.button("Remove Duplicates"):
                df.drop_duplicates(inplace=True)
                st.success("Duplicates removed")
        else:
            st.write("No duplicates found")

    with tabs[2]:
        st.markdown("<h2 style='color: #d62728;'>Visualizations</h2>", unsafe_allow_html=True)
        st.markdown("---")
        graph_type = st.selectbox("Graph Type", ["Line", "Bar", "Scatter", "Box", "Histogram", "Heatmap"])
        x_axis = st.selectbox("X Axis", df.columns)
        y_axis = st.selectbox("Y Axis", numeric_cols)
        group_by = st.selectbox("Group By (Optional)", [None] + df.columns.tolist())

        if st.button("Generate Graph"):
            if graph_type == "Line":
                fig = px.line(df, x=x_axis, y=y_axis, color=group_by)
            elif graph_type == "Bar":
                fig = px.bar(df, x=x_axis, y=y_axis, color=group_by)
            elif graph_type == "Scatter":
                fig = px.scatter(df, x=x_axis, y=y_axis, color=group_by)
            elif graph_type == "Box":
                fig = px.box(df, x=x_axis, y=y_axis, color=group_by)
            elif graph_type == "Histogram":
                fig = px.histogram(df, x=x_axis, y=y_axis, color=group_by)
            elif graph_type == "Heatmap":
                fig = px.imshow(df[numeric_cols].corr())
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown("**Time Series Detection**")
        datetime_cols = df.select_dtypes(include=["datetime", "datetime64"]).columns.tolist()
        if not datetime_cols:
            for col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col])
                    datetime_cols.append(col)
                except:
                    continue

        if datetime_cols:
            dt_col = st.selectbox("Select datetime column", datetime_cols)
            st.line_chart(df.set_index(dt_col)[numeric_cols])

    with tabs[3]:
        st.markdown("<h2 style='color: #9467bd;'>Insights</h2>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**Top Categorical Column Frequencies**")
        for col in categorical_cols:
            with st.expander(f"{col} Frequency"):
                st.write(df[col].value_counts().head())

        st.markdown("---")
        st.markdown("**Auto Summary**")
        summary = f"The dataset has {row_count} rows and {col_count} columns. The numerical columns are: {', '.join(numeric_cols)}."
        if categorical_cols:
            summary += f" The categorical columns include: {', '.join(categorical_cols)}."
        st.info(summary)

        st.markdown("---")
        st.markdown("**AutoML & Feature Importance**")
        target = st.selectbox("Select target column (for ML analysis)", df.columns)
        task_type = st.radio("Task Type", ["Classification", "Clustering"])

        if st.button("Run ML Analysis"):
            if task_type == "Classification":
                s = cls_setup(df, target=target, silent=True, verbose=False, session_id=123)
                best_model = cls_compare()
                st.write("Best Model:")
                st.write(best_model)
                st.write("Feature Importance:")
                st.write(cls_pull().loc[:, ['Variable', 'Importance']])
            elif task_type == "Clustering":
                s = clu_setup(df.dropna(), normalize=True, silent=True, session_id=123)
                kmeans = clu_create('kmeans')
                clustered_df = assign_model(kmeans)
                st.write("Clustered Data Preview:")
                st.write(clustered_df.head())

    with tabs[4]:
        st.markdown("<h2 style='color: #8c564b;'>Export & Share</h2>", unsafe_allow_html=True)
        st.markdown("---")
        towrite = BytesIO()
        df.to_csv(towrite, index=False)
        towrite.seek(0)
        b64 = base64.b64encode(towrite.read()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="cleaned_data.csv">Download Cleaned CSV</a>'
        st.markdown(href, unsafe_allow_html=True)

        st.markdown("**Email Report**")
        email_to = st.text_input("Recipient Email")
        email_subject = st.text_input("Email Subject", "CSV Analysis Report")
        email_content = summary

        if st.button("Send Email"):
            try:
                msg = EmailMessage()
                msg.set_content(email_content)
                msg["Subject"] = email_subject
                msg["From"] = "youremail@example.com"
                msg["To"] = email_to

                with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                    smtp.starttls()
                    smtp.login("youremail@example.com", "yourpassword")
                    smtp.send_message(msg)
                st.success("Email sent successfully")
            except Exception as e:
                st.error(f"Failed to send email: {e}")
else:
    st.info("Please upload a CSV file to begin analysis.")
