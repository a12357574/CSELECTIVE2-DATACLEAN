import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="VisWalis",
    page_icon="assets/viswalis-favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

tab1, tab2, tab3, tab4 = st.tabs(["Data Cleaning", "Dashboard", "Report", "Ask AI"])

st.sidebar.image("assets/viswalis-logo.png")
st.sidebar.subheader("🧹 Brushing Off the Mess, 🌟 Visualizing Success!", anchor=False)
st.sidebar.write("VisWalis simplifies data analysis. Upload a CSV, let us clean it, and explore interactive visualizations.")
st.sidebar.divider()

csv_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])


with tab1:
    st.header("Data Cleaning")
    data_table, buttons = st.columns([4, 1])

    if csv_file:
        df = pd.read_csv(csv_file)

        with data_table:
            st.dataframe(df)  

        with buttons:
            st.button("Standardized Columns")
            st.button("Drop Empty Values")
            st.button("Drop Duplicates")
            st.button("Remove Outliers")
            st.button("Auto Clean")

    else:
        st.warning('Please upload a CSV File!', icon="⚠️")

with tab2:
    st.header("Dashboard")
    
    if csv_file:
        st.subheader("Pie Chart")
        column_for_pie = st.selectbox("Select a column for the Pie Chart:", df.columns)
        pie_chart = px.pie(df, names=column_for_pie)
        st.plotly_chart(pie_chart)

        st.subheader("Area Plot")
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        area_x = st.selectbox("Select X-axis for Area Plot:", numeric_cols)
        area_y = st.multiselect("Select Y-axis for Area Plot:", numeric_cols)
        if area_x and area_y:
            area_plot = px.area(df, x=area_x, y=area_y)
            st.plotly_chart(area_plot)

        st.subheader("Donut Chart")
        column_for_donut = st.selectbox("Select a column for the Donut Chart:", df.columns, key="donut")
        donut_chart = px.pie(df, names=column_for_donut, hole=0.4)
        st.plotly_chart(donut_chart)

        st.subheader("Radar Chart")
        radar_cols = st.multiselect("Select columns for Radar Chart (numeric only):", numeric_cols)
        if len(radar_cols) > 0:
            radar_data = df[radar_cols].mean().reset_index()
            radar_data.columns = ['Metric', 'Value']
            radar_chart = px.line_polar(radar_data, r='Value', theta='Metric', line_close=True)
            st.plotly_chart(radar_chart)

        st.subheader("Gauge Chart")
        gauge_col = st.selectbox("Select a column for Gauge Chart (numeric only):", numeric_cols, key="gauge")
        if gauge_col:
            gauge_value = df[gauge_col].mean()
            fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=gauge_value,
            title={'text': f"Mean of {gauge_col}"},
            gauge={
            'axis': {'range': [0, df[gauge_col].max()]},
            'bar': {'color': "blue"},
            'steps': [
                {'range': [0, df[gauge_col].max() / 2], 'color': "lightgray"},
                {'range': [df[gauge_col].max() / 2, df[gauge_col].max()], 'color': "gray"}
            ],
        }
    ))
        st.plotly_chart(fig)
    else:
        st.warning('Please upload a CSV File to see visualizations!', icon="⚠️")