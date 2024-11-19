import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import h5py as h5
import branca
import datetime
import plot_map as get_map
import useful_functions as uf
import folium
import geopandas as gpd
import branca
from streamlit_folium import st_folium
import os
import matplotlib as mp


# Page configuration
st.set_page_config(
    page_title="PASSAGE Vegetation Condition Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed")

# st.sidebar.success("Select a regio above.")

# pg = st.navigation([st.Page("2_Kenya.py")])
# pg.run()



# ________________________________________
# TITLE
# ________________________________________

colal,  colbe = st.columns([40, 20], vertical_alignment= "center",  gap="small")
with colal:
    st.title('Vegetation Condition Monitoring & Forecasting')
with colbe:
    st.image("PASSAGE CLARE horizontal EN .png", width=500)

st.divider()

# # :earth_africa: VCI3M, NDVI Monitoring & Forecasting
'''
This tool shows historical and forecasted 3-month average vegetation condition index (VCI3M) and the historical Normalized Difference Vegetation Index (NDVI) generated from VIIRS data across PASSAGE's regions of interest.
PASSAGE focuses on 3 of IGAD's cross boundary clusters  (1:Karamoja, 2:Moyale, 3:Mandera)*. To view relevant data, select a cluster from the drop down menu below and click a sub county on the map to see a VCI3M forecast for that region.  

Note: This tool is under active development. 
'''

# ________________________________________
# Sub title forecast VCI3M
# ________________________________________
st.header("Forecasted VCI3M", divider='gray')




# ________________________________________
# Select sub county
# ________________________________________

DATA_SOURCE = "VIIRS"

# SELECT WHICH CLUSTER

clusters = ['Karamoja', "Moyale", "Mandera"]
selected_cluster_name = st.selectbox("Select IGAD Cluster", clusters)

# ______________________________________
# LOAD SELECTED DATA
# ________________________________________

cluster_labels = {'Karamoja': 'CLUSTER_1',
                  "Moyale": "CLUSTER_2",
                  "Mandera": "CLUSTER_3"}

selected_cluster = cluster_labels[selected_cluster_name]

datasets, df, df_NDVI, last_observed_VCI3M, min_date, max_date, dates = uf.load_observed_data(DATA_SOURCE,
                                                                                              selected_cluster)

df_vci_smoothed, df_vci3m_smoothed = uf.load_smoothed_data(DATA_SOURCE, selected_cluster, datasets)

if selected_cluster == "CLUSTER_1":
    shapefile_path = "./shapefiles/IGAD_Cluster_123/IGAD_Cluster_1.shp"
    LEVEL_3_LABEL = "County"
elif selected_cluster == "CLUSTER_2":
    shapefile_path = "./shapefiles/IGAD_Cluster_123/IGAD_Cluster_2.shp"
    LEVEL_3_LABEL = "WOREDANAME"
else:
    shapefile_path = "./shapefiles/IGAD_Cluster_123/IGAD_Cluster_3.shp"
    LEVEL_3_LABEL = "DISTRICT"

st.write("Select a sub county on the map to see VCI3M forecast and historical data for that region  ")

col = st.columns(( 1, 1), gap='medium')

with col[0]:
    # ________________________________________
    # Create map showing selected sub county
    # ________________________________________


    m = uf.create_base_map_passage_clusters()

    shapefile = uf.add_last_observed_VCI3M_to_shapefile(shapefile_path, LEVEL_3_LABEL, last_observed_VCI3M, datasets)

    bounds = [0, 1, 10, 20, 35, 50, 100]

    #
    colormap = branca.colormap.LinearColormap(
        # vmin=0,  # shapefile["VCI3M"].quantile(0.0),
        # vmax=shapefile["VCI3M"].quantile(1),
        colors=["red", "r", "orange", "yellow", "green", "darkgreen"],
        caption="VCI3M",
    ).to_step(index = bounds)

    tooltip = folium.GeoJsonTooltip(
        fields=[LEVEL_3_LABEL, "VCI3M"],
        aliases=["Sub county:", "Latest VCI3M:"],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: #F0EFEF;
            border: 2px solid black;
            border-radius: 3px;
            box-shadow: 3px;
        """,
        max_width=800,
    )

    g = folium.GeoJson(
        shapefile,
        style_function=lambda x: {
            "fillColor": colormap(x["properties"]["VCI3M"])
            if x["properties"]["VCI3M"] is not None
            else "transparent",
            "color": "black",
            "fillOpacity": 0.6,
        },
        tooltip=tooltip,
        # popup=popup,
    ).add_to(m)

    colormap.add_to(m)

    output = st_folium(m, width=700, height=500)

    # state_name = ''
    if output['last_active_drawing']:
        selected_coulum = output["last_object_clicked_tooltip"].splitlines()[3].lstrip()
        # st.write(selected_coulum)
    else:
        selected_coulum = datasets[0]


    # if output["last_object_clicked_tooltip"] == None:
    #     pass
    # else :
    #     st.write(output["last_object_clicked_tooltip"])



with col[1]:

    # ________________________________________
    # calculate errors from hindcasts for this subcounty
    # ________________________________________
    errors = uf.get_error(DATA_SOURCE, selected_cluster,selected_coulum)


    df_forecasts_T = uf.load_forecasted_VCI3M(DATA_SOURCE, selected_cluster)
    dates_forecast = list(df_forecasts_T[selected_coulum].index)
    VCI3M_forecast = list(df_forecasts_T[selected_coulum].values)

    historical_smoothed_VCI3M = list(df_vci3m_smoothed[selected_coulum].values)
    # VCI3M = list(df[selected_coulum].values)

    # ________________________________________
    # # Create figures showing forecasted VCI3M
    # # ________________________________________
    fig3, ax3 = uf.plot_forecasts(dates, historical_smoothed_VCI3M, dates_forecast,VCI3M_forecast, errors, max_date, selected_coulum)

    st.pyplot(fig3)




st.header(f"Historical data {selected_coulum} ", divider='gray')

# # ________________________________________
# # Slider to select time period
# # ________________________________________

from_date, to_date = st.slider(
    'Which time period are you interested in?',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date])

# Filter the data
filtered_df = df.loc[from_date:to_date]
filtered_df_NDVI = df_NDVI.loc[from_date:to_date]



col_historical = st.columns(( 1, 1), gap='medium')
with col_historical[0]:
    # # ________________________________________
    # # Create figures showing historical VCI3M
    # # ________________________________________
    st.subheader("Historical weekly VCI3M ", divider='gray')
    tab1, tab2 = st.tabs(["Chart", "Data"])

    with tab1:
        # streamlit line chart
        # st.subheader("Historical weekly VCI3M ", divider='gray')
        st.line_chart(filtered_df[selected_coulum], x_label="Date", y_label="VCI3M")
    with tab2:
        # ________________________________________
        # Display VCI3M dataframe
        # ________________________________________
        # st.subheader("Historical weekly VCI3M dataframe for all regions ", divider='gray')

        st.dataframe(filtered_df)

with col_historical[1]:

    # # ________________________________________
    # # Display historical NDVI
    # # ________________________________________
    st.subheader("Historical weekly NDVI", divider='gray')
    tab1_2, tab2_2 =  st.tabs(["Chart", "Data"])
    with tab1_2:

        # streamlit line chart
        st.line_chart(filtered_df_NDVI[selected_coulum], x_label="Date", y_label="NDVI")

    with tab2_2:
        # st.subheader("Historical weekly NDVI all regions ", divider='gray')
        # streamlit line chart
        st.dataframe(filtered_df_NDVI)





#
#
# # # amtplotlib mine graph
# # fig2, ax2 = plt.subplots(figsize=(10, 7))
# # ax2 = filtered_df[selected_coulum].plot(color='black' )
# #
# # ax2.set_ylim(0 , 100)
# # ax2.set_ylim(0, 120 )
# #
# # ax2.set_xlabel("Time")
# # ax2.set_ylabel("VCI3M")
# #
# # ax2.axhspan(0, 10, alpha=0.5, color="r")
# # ax2.axhspan(10, 20, alpha=0.5, color="darkorange")
# # ax2.axhspan(20, 35, alpha=0.5, color="yellow")
# # ax2.axhspan(35, 50, alpha=0.5, color="limegreen")
# # ax2.axhspan(50, 300, alpha=0.5, color="darkgreen")
# # st.pyplot(fig2)
#
#
#
#
#
'''
(*) The boundaries and names shown on these maps do not imply the expression of any opinion whatsoever concerning the legal status of any
country, territory, city or area or of its authorities, or concerning the delimitation of its frontiers and boundaries
'''




# #
# # fig, ax = get_map.create_map(selected_coulum ,shapefile_path,last_observed_VCI3M[selected_coulum],LEVEL_3_LABEL )
# #
# # with col2:
# #     st.pyplot(fig, use_container_width=False)
#