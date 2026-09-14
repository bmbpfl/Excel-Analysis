import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Dynamic Data Analysis Tool",
    layout="wide"
)

st.title("📊 CSV / Excel Data Analysis Tool")

# -------------------------------
# File Upload
# -------------------------------
uploaded_file = st.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx", "xls"]
)

# -------------------------------
# Read File Function
# -------------------------------
@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    return df

# -------------------------------
# Main Processing
# -------------------------------
if uploaded_file is not None:

    try:
        df = load_data(uploaded_file)

        # -------------------------------
        # Identify Column Types
        # -------------------------------
        numeric_columns = df.select_dtypes(
            include=[np.number]
        ).columns.tolist()

        text_columns = df.select_dtypes(
            exclude=[np.number]
        ).columns.tolist()

        all_columns = df.columns.tolist()

        # -------------------------------
        # Tabs
        # -------------------------------
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "1️⃣ File Details",
            "2️⃣ Filter Columns",
            "3️⃣ Group & Aggregate",
            "4️⃣ Consolidated Result",
            "5️⃣ Pivot Table",
            "6️⃣ Charts"
        ])

        # ======================================================
        # TAB 1 : FILE DETAILS
        # ======================================================
        with tab1:

            st.subheader("📄 File Details")

            col1, col2, col3 = st.columns(3)

            col1.metric("Rows", df.shape[0])
            col2.metric("Columns", df.shape[1])
            col3.metric("Numeric Columns", len(numeric_columns))

            st.write("### Column Information")

            info_df = pd.DataFrame({
                "Column Name": df.columns,
                "Data Type": df.dtypes.astype(str),
                "Null Count": df.isnull().sum().values
            })

            st.dataframe(info_df, use_container_width=True)

            st.write("### Preview Data")
            st.dataframe(df.head(20), use_container_width=True)

            st.write("### Numeric Columns Identified")
            st.success(numeric_columns if numeric_columns else "No Numeric Columns Found")

            st.write("### Text Columns Identified")
            st.success(text_columns if text_columns else "No Text Columns Found")

        # ======================================================
        # TAB 2 : FILTER COLUMNS
        # ======================================================
        with tab2:

            st.subheader("🔍 Select Columns to Display")

            selected_display_columns = st.multiselect(
                "Choose Columns",
                options=all_columns,
                default=all_columns[:min(5, len(all_columns))]
            )

            if selected_display_columns:
                filtered_df = df[selected_display_columns]
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.warning("Please select at least one column.")

        # ======================================================
        # TAB 3 : GROUP & AGGREGATE
        # ======================================================
        with tab3:

            st.subheader("📌 Group By and Aggregate")

            st.write("### Group By Columns (Text Columns)")

            groupby_columns = st.multiselect(
                "Select Group By Columns",
                options=text_columns,
                default=text_columns[:1] if text_columns else []
            )

            st.write("### Aggregate Columns (Numeric Columns)")

            aggregate_columns = st.multiselect(
                "Select Aggregate Columns",
                options=numeric_columns,
                default=numeric_columns[:1] if numeric_columns else []
            )

            aggregation_function = st.selectbox(
                "Select Aggregation Function",
                options=["sum", "mean", "count", "min", "max"]
            )

            if groupby_columns and aggregate_columns:

                grouped_df = (
                    df.groupby(groupby_columns)[aggregate_columns]
                    .agg(aggregation_function)
                    .reset_index()
                )

                st.write("### Grouped Result")
                st.dataframe(grouped_df, use_container_width=True)

            else:
                st.info("Select Group By and Aggregate columns.")

        # ======================================================
        # TAB 4 : CONSOLIDATED RESULT
        # ======================================================
        with tab4:

            st.subheader("📊 Consolidated Analysis Result")

            # Column Filter
            selected_display_columns_final = st.multiselect(
                "Select Columns to Display",
                options=all_columns,
                default=all_columns,
                key="final_display_cols"
            )

            # Group By
            groupby_columns_final = st.multiselect(
                "Select Group By Columns",
                options=text_columns,
                default=text_columns[:1] if text_columns else [],
                key="final_groupby"
            )

            # Aggregate Columns
            aggregate_columns_final = st.multiselect(
                "Select Aggregate Columns",
                options=numeric_columns,
                default=numeric_columns[:1] if numeric_columns else [],
                key="final_agg"
            )

            aggregation_function_final = st.selectbox(
                "Aggregation Function",
                options=["sum", "mean", "count", "min", "max"],
                key="final_func"
            )

            result_df = df.copy()

            # Apply display column filter
            if selected_display_columns_final:
                result_df = result_df[selected_display_columns_final]

            # Apply Group By + Aggregate
            if groupby_columns_final and aggregate_columns_final:

                result_df = (
                    df.groupby(groupby_columns_final)[aggregate_columns_final]
                    .agg(aggregation_function_final)
                    .reset_index()
                )

            st.write("### Final Consolidated Result")

            st.dataframe(result_df, use_container_width=True)

            # Download option
            csv = result_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇ Download Result CSV",
                data=csv,
                file_name="analysis_result.csv",
                mime="text/csv"
            )

        # ======================================================
        # TAB 5 : PIVOT TABLE
        # ======================================================
        with tab5:

            st.subheader("📈 Pivot Table")

            pivot_index = st.multiselect(
                "Select Index Columns",
                options=text_columns,
                default=text_columns[:1] if text_columns else []
            )

            pivot_columns = st.multiselect(
                "Select Pivot Columns",
                options=text_columns,
                default=text_columns[1:2] if len(text_columns) > 1 else []
            )

            pivot_values = st.multiselect(
                "Select Value Columns",
                options=numeric_columns,
                default=numeric_columns[:1] if numeric_columns else []
            )

            pivot_aggfunc = st.selectbox(
                "Pivot Aggregation Function",
                options=["sum", "mean", "count", "min", "max"]
            )

            if pivot_index and pivot_values:

                pivot_df = pd.pivot_table(
                    df,
                    index=pivot_index,
                    columns=pivot_columns if pivot_columns else None,
                    values=pivot_values,
                    aggfunc=pivot_aggfunc,
                    fill_value=0
                )

                st.write("### Pivot Table Result")

                st.dataframe(
                    pivot_df,
                    use_container_width=True
                )

                # Excel download for pivot table
                excel_buffer = io.BytesIO()
                pivot_df.to_excel(excel_buffer, index=True, engine="openpyxl")
                excel_buffer.seek(0)

                st.download_button(
                    label="⬇ Download Pivot Table as Excel",
                    data=excel_buffer,
                    file_name="pivot_table.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            else:
                st.info("Please select Index and Value columns.")

        # ======================================================
        # TAB 6 : CHARTS
        # ======================================================
        with tab6:

            st.subheader("📉 Charts")

            chart_type = st.selectbox(
                "Select Chart Type",
                options=[
                    "Bar Chart",
                    "Line Chart",
                    "Scatter Plot",
                    "Pie Chart",
                    "Area Chart",
                    "Histogram",
                    "Box Plot",
                    "Heatmap (Correlation)"
                ]
            )

            if chart_type == "Heatmap (Correlation)":

                if len(numeric_columns) < 2:
                    st.warning("Need at least 2 numeric columns for a correlation heatmap.")
                else:
                    selected_corr_cols = st.multiselect(
                        "Select Numeric Columns",
                        options=numeric_columns,
                        default=numeric_columns[:min(6, len(numeric_columns))]
                    )

                    if len(selected_corr_cols) >= 2:
                        corr_matrix = df[selected_corr_cols].corr()
                        fig = px.imshow(
                            corr_matrix,
                            text_auto=".2f",
                            color_continuous_scale="RdBu_r",
                            zmin=-1, zmax=1,
                            title="Correlation Heatmap"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Select at least 2 numeric columns.")

            elif chart_type == "Histogram":

                hist_col = st.selectbox(
                    "Select Column",
                    options=numeric_columns
                )
                num_bins = st.slider("Number of Bins", min_value=5, max_value=100, value=20)

                if hist_col:
                    fig = px.histogram(
                        df,
                        x=hist_col,
                        nbins=num_bins,
                        title=f"Histogram of {hist_col}",
                        color_discrete_sequence=["#636EFA"]
                    )
                    st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Pie Chart":

                pie_label_col = st.selectbox(
                    "Select Label Column (Text)",
                    options=text_columns if text_columns else all_columns
                )
                pie_value_col = st.selectbox(
                    "Select Value Column (Numeric)",
                    options=numeric_columns
                )

                if pie_label_col and pie_value_col:
                    pie_data = (
                        df.groupby(pie_label_col)[pie_value_col]
                        .sum()
                        .reset_index()
                    )
                    fig = px.pie(
                        pie_data,
                        names=pie_label_col,
                        values=pie_value_col,
                        title=f"{pie_value_col} by {pie_label_col}"
                    )
                    st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Box Plot":

                box_y_col = st.selectbox(
                    "Select Numeric Column (Y-axis)",
                    options=numeric_columns
                )
                box_x_col = st.selectbox(
                    "Select Category Column (X-axis, optional)",
                    options=["None"] + text_columns
                )

                if box_y_col:
                    fig = px.box(
                        df,
                        x=box_x_col if box_x_col != "None" else None,
                        y=box_y_col,
                        title=f"Box Plot of {box_y_col}"
                            + (f" by {box_x_col}" if box_x_col != "None" else ""),
                        color=box_x_col if box_x_col != "None" else None
                    )
                    st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Scatter Plot":

                scatter_x = st.selectbox("X-axis Column", options=numeric_columns, key="sc_x")
                scatter_y = st.selectbox(
                    "Y-axis Column",
                    options=numeric_columns,
                    index=min(1, len(numeric_columns) - 1),
                    key="sc_y"
                )
                scatter_color = st.selectbox(
                    "Color By (optional)",
                    options=["None"] + text_columns,
                    key="sc_color"
                )

                if scatter_x and scatter_y:
                    fig = px.scatter(
                        df,
                        x=scatter_x,
                        y=scatter_y,
                        color=scatter_color if scatter_color != "None" else None,
                        title=f"{scatter_y} vs {scatter_x}",
                        opacity=0.7
                    )
                    st.plotly_chart(fig, use_container_width=True)

            else:
                # Bar, Line, Area charts share same axis config
                x_col = st.selectbox(
                    "Select X-axis Column",
                    options=all_columns,
                    index=0
                )
                y_cols = st.multiselect(
                    "Select Y-axis Column(s) (Numeric)",
                    options=numeric_columns,
                    default=numeric_columns[:min(2, len(numeric_columns))]
                )
                color_col = st.selectbox(
                    "Color By (optional, for single Y)",
                    options=["None"] + text_columns,
                    key="main_color"
                )

                if x_col and y_cols:
                    color_arg = color_col if (color_col != "None" and len(y_cols) == 1) else None

                    if chart_type == "Bar Chart":
                        fig = px.bar(
                            df,
                            x=x_col,
                            y=y_cols,
                            color=color_arg,
                            title=f"Bar Chart — {', '.join(y_cols)} by {x_col}",
                            barmode="group"
                        )

                    elif chart_type == "Line Chart":
                        fig = px.line(
                            df,
                            x=x_col,
                            y=y_cols,
                            color=color_arg,
                            title=f"Line Chart — {', '.join(y_cols)} over {x_col}",
                            markers=True
                        )

                    elif chart_type == "Area Chart":
                        fig = px.area(
                            df,
                            x=x_col,
                            y=y_cols,
                            color=color_arg,
                            title=f"Area Chart — {', '.join(y_cols)} over {x_col}"
                        )

                    fig.update_layout(legend_title_text="")
                    st.plotly_chart(fig, use_container_width=True)

                else:
                    st.info("Please select X-axis and at least one Y-axis column.")

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

else:
    st.info("Please upload a CSV or Excel file to begin analysis.")