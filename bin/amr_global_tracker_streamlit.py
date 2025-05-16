
#!/usr/bin/env python3

import pandas as pd
import streamlit as st
import pycountry
import plotly.express as px

st.set_page_config(page_title="AMR Surveillance Dashboard", layout="wide")

st.title("🌍 AMR Surveillance Dashboard")

uploaded_file = st.file_uploader("Upload a TSV file containing AMR data", type=["tsv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, sep="\t")
    df = df.dropna(subset=["tbprofiler_dr_type", "Country_of_sample_collection"])

    # Normalize resistance_genes
    df["resistance_gene_list"] = df["tbprofiler_resistance_genes"].fillna("").apply(lambda x: list(set(x.split(","))))

    # Standardize country names
    def get_country_code(name):
        try:
            return pycountry.countries.lookup(name).name
        except:
            return name
    df["Country_standardized"] = df["Country_of_sample_collection"].apply(get_country_code)

    # Sidebar Filters
    st.sidebar.title("Filters")
    selected_country = st.sidebar.multiselect("Select Country", sorted(df["Country_standardized"].unique()))
    selected_amr_type = st.sidebar.multiselect("Select AMR Type", sorted(df["tbprofiler_dr_type"].unique()))
    selected_lineage = st.sidebar.multiselect("Select Lineage", sorted(df["tbprofiler_main_lineage"].dropna().unique()))

    filtered_df = df.copy()
    if selected_country:
        filtered_df = filtered_df[filtered_df["Country_standardized"].isin(selected_country)]
    if selected_amr_type:
        filtered_df = filtered_df[filtered_df["tbprofiler_dr_type"].isin(selected_amr_type)]
    if selected_lineage:
        filtered_df = filtered_df[filtered_df["tbprofiler_main_lineage"].isin(selected_lineage)]

    # World Map
    map_data = filtered_df.groupby("Country_standardized").size().reset_index(name="Sample Count")
    fig_map = px.choropleth(map_data,
                            locations="Country_standardized",
                            locationmode="country names",
                            color="Sample Count",
                            title="Sample Distribution by Country",
                            color_continuous_scale="Reds")
    st.plotly_chart(fig_map, use_container_width=True)

    # Bar Chart: AMR Types
    amr_counts = filtered_df["tbprofiler_dr_type"].value_counts().reset_index()
    amr_counts.columns = ["Resistance Type", "Count"]
    fig_bar = px.bar(amr_counts, x="Resistance Type", y="Count", title="Distribution of AMR Types")
    st.plotly_chart(fig_bar, use_container_width=True)

    # Bar Chart: Lineage
    if "tbprofiler_main_lineage" in filtered_df.columns:
        lineage_counts = filtered_df["tbprofiler_main_lineage"].value_counts().reset_index()
        lineage_counts.columns = ["Lineage", "Count"]
        fig_lineage = px.bar(lineage_counts, x="Lineage", y="Count", title="Lineage Distribution")
        st.plotly_chart(fig_lineage, use_container_width=True)
else:
    st.info("Please upload a .tsv file to begin.")
