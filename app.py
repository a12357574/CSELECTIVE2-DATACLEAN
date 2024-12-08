import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import os
# Data Cleaning Imports
from utils.data_cleaner import DataCleaner as dc

# Page Configuration
st.set_page_config(
    page_title="VisWalis",
    page_icon="assets/viswalis-favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for DataFrame and uploaded file name
if 'df' not in st.session_state:
    st.session_state.df = None
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

# Define the function to generate the PDF report
def generate_pdf_report(dataframe, file_name="data_report.pdf"):
    """
    Generates a PDF report for the given DataFrame with visualizations.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title Page
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 10, txt="Data Report", ln=True, align="C")
    pdf.ln(10)

    # Summary Statistics
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt="Summary Statistics:", ln=True)
    pdf.ln(5)

    try:
        summary = dataframe.describe(include="all").transpose()
        summary.reset_index(inplace=True)
        summary.columns = ["Feature", "Count", "Mean", "Std", "Min", "25%", "50%", "75%", "Max"]

        for _, row in summary.iterrows():
            pdf.set_font("Courier", size=10)
            pdf.cell(0, 10, txt=row.to_string(index=False), ln=True)
        pdf.ln(10)
    except Exception as e:
        pdf.cell(0, 10, txt=f"Error generating summary: {e}", ln=True)
        pdf.ln(10)

    # Data Preview
    pdf.cell(0, 10, txt="Data Preview (First 5 Rows):", ln=True)
    pdf.ln(5)
    preview_text = dataframe.head().to_string(index=False)
    pdf.set_font("Courier", size=10)
    pdf.multi_cell(0, 10, txt=preview_text)
    pdf.ln(10)

    # Visualizations
    pdf.cell(0, 10, txt="Visualizations:", ln=True)
    pdf.ln(5)

    numeric_columns = dataframe.select_dtypes(include=["float64", "int64"]).columns.tolist()

    # Pie Chart
    try:
        pie_col = numeric_columns[0] if numeric_columns else None
        if pie_col:
            pie_fig = px.pie(dataframe, names=pie_col, title=f"Pie Chart of {pie_col}")
            pie_file = "pie_chart.png"
            pie_fig.write_image(pie_file)
            pdf.image(pie_file, x=10, y=pdf.get_y(), w=180)
            pdf.ln(90)
            os.remove(pie_file)
    except Exception as e:
        pdf.cell(0, 10, txt=f"Error generating pie chart: {e}", ln=True)

    # Area Plot
    try:
        if numeric_columns:
            plt.figure(figsize=(8, 4))
            dataframe[numeric_columns].plot(kind="area", alpha=0.5)
            plt.title("Area Plot")
            plt.tight_layout()
            area_plot_file = "area_plot.png"
            plt.savefig(area_plot_file)
            plt.close()
            pdf.image(area_plot_file, x=10, y=pdf.get_y(), w=180)
            pdf.ln(90)
            os.remove(area_plot_file)
    except Exception as e:
        pdf.cell(0, 10, txt=f"Error generating area plot: {e}", ln=True)

    # Donut Chart
    try:
        if numeric_columns:
            mean_values = dataframe[numeric_columns].mean()
            donut_data = pd.DataFrame({"Metric": mean_values.index, "Value": mean_values.values})
            donut_fig = px.pie(donut_data, names="Metric", values="Value", hole=0.4, title="Donut Chart of Averages")
            donut_file = "donut_chart.png"
            donut_fig.write_image(donut_file)
            pdf.image(donut_file, x=10, y=pdf.get_y(), w=180)
            pdf.ln(90)
            os.remove(donut_file)
    except Exception as e:
        pdf.cell(0, 10, txt=f"Error generating donut chart: {e}", ln=True)

    # Radar Chart
    try:
        if numeric_columns:
            radar_data = dataframe[numeric_columns].mean().reset_index()
            radar_data.columns = ["Metric", "Value"]
            radar_data["Normalized"] = (radar_data["Value"] - radar_data["Value"].min()) / (
                radar_data["Value"].max() - radar_data["Value"].min()
            )

            radar_fig = px.line_polar(
                radar_data, r="Normalized", theta="Metric", line_close=True, title="Radar Chart of Averages"
            )
            radar_file = "radar_chart.png"
            radar_fig.write_image(radar_file)
            pdf.image(radar_file, x=10, y=pdf.get_y(), w=180)
            pdf.ln(90)
            os.remove(radar_file)
    except Exception as e:
        pdf.cell(0, 10, txt=f"Error generating radar chart: {e}", ln=True)

    # Gauge Chart
    try:
        if numeric_columns:
            gauge_col = numeric_columns[0]  # Use the first numeric column for the gauge
            gauge_value = dataframe[gauge_col].mean()
            gauge_fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=gauge_value,
                title={'text': f"Gauge of {gauge_col}"},
                gauge={'axis': {'range': [0, dataframe[gauge_col].max() * 1.1]}}
            ))
            gauge_file = "gauge_chart.png"
            gauge_fig.write_image(gauge_file)
            pdf.image(gauge_file, x=10, y=pdf.get_y(), w=180)
            pdf.ln(90)
            os.remove(gauge_file)
    except Exception as e:
        pdf.cell(0, 10, txt=f"Error generating gauge chart: {e}", ln=True)

    # Save the PDF
    pdf.output(file_name)


# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Data Cleaning", "Dashboard", "Report", "Ask AI"])

# Sidebar
st.sidebar.image("assets/viswalis-logo.png")
st.sidebar.subheader("🧹 Brushing Off the Mess, 🌟 Visualizing Success!", anchor=False)
st.sidebar.write("VisWalis simplifies data analysis. Upload a CSV, let us clean it, and explore interactive visualizations.")
st.sidebar.divider()

# File uploader
csv_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

# Check if a new file is uploaded
if csv_file:
    if st.session_state.uploaded_file_name != csv_file.name:
        st.session_state.df = pd.read_csv(csv_file)
        st.session_state.uploaded_file_name = csv_file.name
        alert = f"Loaded new CSV: {csv_file.name}"
else:
    st.warning('Please load a CSV File!', icon="⚠️")



# Main Content
if st.session_state.df is not None:
    with tab1:
        st.header("Data Cleaning", anchor=False)

        # Cleaner instance
        cleaner = dc(st.session_state.df)

        # Display the CSV title
        st.subheader(f"Loaded CSV: {st.session_state.uploaded_file_name}", anchor=False)

        # Layout: Two columns (left for DataFrame, right for tools)
        col1, col2 = st.columns([3, 1])

        with col1:
            # Display the current DataFrame
            st.subheader("Current Data", anchor=False)
            st.dataframe(st.session_state.df)

        with col2:
            # Tools Section
            st.subheader("Tools", anchor=False)
            
            btn1, btn2 = st.columns([0.5,0.5])
            with btn1:
                if st.button("Refresh Table"):
                    st.session_state.df = st.session_state.df # Refresh the CSV
                    alert = "Table is Refreshed!"
            with btn2: 

                @st.cache_data
                def convert_df(df):
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    return df.to_csv().encode("utf-8")

                csv = convert_df(st.session_state.df)

                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name= f"{st.session_state.uploaded_file_name}[cleaned_data].csv",
                    mime="text/csv",
                )

            # Edit Columns Section
            with st.expander("Edit Columns"):
                st.subheader("Standardize Column Names")
                # Options for standardizing column names
                standardize_case = st.radio("Select case for column names:", ["lowercase", "uppercase", "sentence case"])
                replace_text = st.text_input("Text to replace in column names:")
                replacement_text = st.text_input("Replace with:")
                if st.button("Apply Standardization"):
                    if standardize_case == "lowercase":
                        st.session_state.df.columns = (
                            st.session_state.df.columns
                            .str.strip()
                            .str.lower()
                            .str.replace(replace_text, replacement_text)
                        )
                    elif standardize_case == "uppercase":
                        st.session_state.df.columns = (
                            st.session_state.df.columns
                            .str.strip()
                            .str.upper()
                            .str.replace(replace_text, replacement_text)
                        )
                    elif standardize_case == "sentence case":
                        st.session_state.df.columns = (
                            st.session_state.df.columns
                            .str.strip()
                            .str.title()
                            .str.replace(replace_text, replacement_text)
                        )
                    alert = "Column names standardized!"

                # Drop Column
                st.subheader("Drop Columns")
                column_to_drop = st.selectbox("Select column to drop:", st.session_state.df.columns)
                if st.button("Drop Column"):
                    st.session_state.df = st.session_state.df.drop(columns=[column_to_drop])
                    alert = f"Column '{column_to_drop}' dropped!"

            # Handle Missing Values Section
            with st.expander("Handle Missing Values"):
                st.subheader("Handle Missing Data")
                strategy = st.radio("Select strategy to handle missing values:", ["drop", "mean", "median", "mode", "fill"])
                if strategy == "fill":
                    fill_value = st.text_input("Value to fill missing data with:")
                    column_to_handle = st.selectbox("Select column to handle:", st.session_state.df.columns)

                if st.button("Apply Missing Value Handling"):
                    if strategy == "drop":
                        st.session_state.df = cleaner.handle_missing_values(strategy="drop").get_cleaned_data()
                    elif strategy == "mean":
                        st.session_state.df = cleaner.handle_missing_values(strategy="mean").get_cleaned_data()
                    elif strategy == "median":
                        st.session_state.df = cleaner.handle_missing_values(strategy="median").get_cleaned_data()
                    elif strategy == "mode":
                        st.session_state.df = cleaner.handle_missing_values(strategy="mode").get_cleaned_data()
                    elif strategy == "fill" and fill_value:
                        st.session_state.df[column_to_handle] = st.session_state.df[column_to_handle].fillna(fill_value)
                    alert = f"Missing values handled using strategy '{strategy}'!"

            # Drop Duplicates Section
            with st.expander("Drop Duplicates"):
                if st.button("Drop Duplicate Rows"):
                    st.session_state.df = cleaner.drop_duplicates().get_cleaned_data()
                    alert = "Duplicate rows removed!"

            # Remove Outliers Section
            with st.expander("Remove Outliers"):
                st.subheader("Remove Outliers")
                column_for_outliers = st.selectbox("Select column to check for outliers:", st.session_state.df.select_dtypes(include=[float, int]).columns)
                if st.button("Remove Outliers"):
                    st.session_state.df = cleaner.remove_outliers(columns=[column_for_outliers]).get_cleaned_data()
                    alert = f"Outliers removed from column '{column_for_outliers}'!"


        # Success Alert
        try:
            st.success(alert)
        except NameError:
            pass

# Dashboard - Visualization
with tab2:
    st.header("Dashboard")
    
   
    if csv_file:
        # Example Pie Chart
        st.subheader("Pie Chart")
        column_for_pie = st.selectbox("Select a column for the Pie Chart:", st.session_state.df.columns)
        pie_chart = px.pie(st.session_state.df, names=column_for_pie)
        st.plotly_chart(pie_chart)

        # Example Area Plot
        st.subheader("Area Plot")
        sequential_cols = [
        col for col in st.session_state.df.columns
        if st.session_state.df[col].dtype in ['object', 'datetime64[ns]']
        or st.session_state.df[col].is_monotonic_increasing  # Checks for ascending order
    ]

        # Detect numeric columns for the Y-axis
        numeric_cols_for_area = st.session_state.df.select_dtypes(include=['float64', 'int64']).columns

        # X-axis selection
        if sequential_cols:
            area_x = st.selectbox("Select X-axis for Area Plot (e.g., time, quarters):", sequential_cols)
        else:
            st.warning("No suitable sequential data found for the X-axis. Area plot cannot be generated.", icon="⚠️")
            area_x = None

        # Y-axis selection (multiple numeric columns allowed)
        if numeric_cols_for_area.any():
            area_y = st.multiselect("Select Y-axis for Area Plot (e.g., numerical data):", numeric_cols_for_area)
        else:
            st.warning("No numerical columns found for the Y-axis. Area plot cannot be generated.", icon="⚠️")
            area_y = []

        # Generate Area Plot if valid selections exist
        if area_x and area_y:
            # Rescale large Y-values to a readable range (e.g., thousands, millions)
            df_rescaled = st.session_state.df.copy()
            for col in area_y:
                max_val = df_rescaled[col].max()
                if max_val > 1e6:  # Millions
                    df_rescaled[col] = df_rescaled[col] / 1e6
                    df_rescaled.rename(columns={col: f"{col} (in millions)"}, inplace=True)
                elif max_val > 1e3:  # Thousands
                    df_rescaled[col] = df_rescaled[col] / 1e3
                    df_rescaled.rename(columns={col: f"{col} (in thousands)"}, inplace=True)

            # Generate the area plot
            area_plot = px.area(
                df_rescaled,
                x=area_x,
                y=area_y,
                title="Area Plot",
                labels={area_x: "X-Axis (Sequential Data)", "value": "Y-Axis (Scaled)"}
            )
            st.plotly_chart(area_plot)
        else:
            st.warning("Please select both a valid X-axis and at least one Y-axis to generate the Area Plot.", icon="⚠️")

        # Updated Donut Chart
        st.subheader("Donut Chart")

        # Get all numeric columns for selection
        numeric_cols_for_donut = st.session_state.df.select_dtypes(include=['float64', 'int64']).columns

        # Multi-select for numeric columns to include in the donut chart
        columns_for_donut = st.multiselect(
            "Select columns for Donut Chart (e.g., grades):", numeric_cols_for_donut
        )

        # If only one column is selected
        if len(columns_for_donut) == 1:
            # Calculate statistics for the selected column
            selected_column = columns_for_donut[0]
            mean_value = st.session_state.df[selected_column].mean()
            median_value = st.session_state.df[selected_column].median()

            # Create a DataFrame for visualization
            fallback_data = pd.DataFrame({
                'Metric': ['Mean', 'Median'],
                'Value': [mean_value, median_value]
            })

            # Generate the donut chart
            fallback_chart = px.pie(
                fallback_data,
                names='Metric',  # Use metrics as labels
                values='Value',  # Use values as slice sizes
                hole=0.4,  # Create the donut hole
                title=f"Summary of {selected_column}"
            )

            # Display the fallback chart
            st.plotly_chart(fallback_chart)

        # If more than one column is selected
        elif len(columns_for_donut) > 1:
            # Compute the mean for the selected columns
            averages = st.session_state.df[columns_for_donut].mean()

            # Create a DataFrame for visualization
            donut_data = pd.DataFrame({
                'Subject': averages.index,  # Column names
                'Average': averages.values  # Corresponding averages
            })

            # Generate the donut chart
            donut_chart = px.pie(
                donut_data,
                names='Subject',  # Use column names as labels
                values='Average',  # Use averages as slice sizes
                hole=0.4,  # Create the donut hole
                title="Average of Columns"
            )

            # Display the chart
            st.plotly_chart(donut_chart)

        # If no column is selected
        else:
            st.warning("Please select at least one column to generate the Donut Chart.", icon="⚠️")

        # Example Radar Chart
        st.subheader("Radar Chart")
        radar_cols = st.multiselect("Select columns for Radar Chart (numeric only):", numeric_cols_for_area)

        if len(radar_cols) > 0:
            # Let user choose aggregation method
            aggregation_method = st.radio("Aggregation Method:", ["Mean", "Median", "Sum"])
            if aggregation_method == "Mean":
                radar_data = st.session_state.df[radar_cols].mean().reset_index()
            elif aggregation_method == "Median":
                radar_data = st.session_state.df[radar_cols].median().reset_index()
            else:
                radar_data = st.session_state.df[radar_cols].sum().reset_index()

            # Rename the columns properly
            radar_data.columns = ['Metric', 'Value']

            # Normalize values for better comparison
            radar_data['Normalized Value'] = (radar_data['Value'] - radar_data['Value'].min()) / \
                                            (radar_data['Value'].max() - radar_data['Value'].min())

            # Generate the radar chart
            radar_chart = px.line_polar(radar_data, r='Normalized Value', theta='Metric', line_close=True)
            st.plotly_chart(radar_chart)
        else:
            st.warning("Please select at least one column for the Radar Chart.", icon="⚠️")


        # Example Gauge Chart
        st.subheader("Gauge Chart")
        gauge_col = st.selectbox("Select a column for Gauge Chart (numeric only):", numeric_cols_for_area, key="gauge")

        if gauge_col:
            # Allow the user to choose which metric to display
            gauge_metric = st.radio("Gauge Metric:", ["Mean", "Median", "Max"])
            if gauge_metric == "Mean":
                gauge_value = st.session_state.df[gauge_col].mean()
            elif gauge_metric == "Median":
                gauge_value = st.session_state.df[gauge_col].median()
            elif gauge_metric == "Max":
                gauge_value = st.session_state.df[gauge_col].max()

            # Automatically determine the gauge range
            gauge_min = 0  # Minimum is always 0
            gauge_max = st.session_state.df[gauge_col].max() * 1.1  # Add 10% buffer to max for better visualization

            # Create the gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=gauge_value,
                title={'text': f"{gauge_metric} of {gauge_col}"},
                gauge={
                    'axis': {'range': [gauge_min, gauge_max]},
                    'bar': {'color': "blue"},
                    'steps': [
                        {'range': [gauge_min, (gauge_min + gauge_max) / 2], 'color': "lightgray"},
                        {'range': [(gauge_min + gauge_max) / 2, gauge_max], 'color': "gray"}
                    ],
                }
            ))

            # Display the chart
            st.plotly_chart(fig)
        else:
            st.warning("Please select a column to generate the Gauge Chart.", icon="⚠️")

# Tab 3: Report
with tab3:
    st.header("Report")

    if st.session_state.df is not None:
        st.subheader("Generate PDF Report")

        # Instructions for the user
        st.write("Click the button below to generate a comprehensive PDF report of your dataset, including summary statistics and visualizations.")

        if st.button("Generate PDF Report"):
            # Generate the PDF report
            generate_pdf_report(st.session_state.df)

            # Success message
            st.success("PDF report generated successfully!")

            # Provide a download button
            with open("data_report.pdf", "rb") as pdf_file:
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_file.read(),
                    file_name="data_report.pdf",
                    mime="application/pdf",
                )
    else:
        st.warning("Please upload and clean the data in the first two tabs before generating the report.")
