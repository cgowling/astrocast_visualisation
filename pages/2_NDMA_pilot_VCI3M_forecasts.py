import streamlit as st
import streamlit as st
import time
import numpy as np
import useful_functions as uf
from streamlit_folium import st_folium

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
import glob
import os

# import sys
# sys.path.append('./../')

st.set_page_config(
    page_title="Kenya vegetation condition",
    layout="wide",
    initial_sidebar_state="expanded")

# ________________________________________
# TITLE
# ________________________________________

colal,  colbe = st.columns([40, 20], vertical_alignment= "center",  gap="small")
with colal:
    st.title('Vegetation Condition Monitoring & Forecasting')
with colbe:
    st.image("PASSAGE CLARE horizontal EN .png", width=500)

st.divider()

st.header('Kenya, NDMA pilot OND 2024')

DATA_SOURCE = "VIIRS"

region = "Kenya"

datasets, df, df_NDVI, last_observed_VCI3M, min_date, max_date, dates = uf.load_observed_data(DATA_SOURCE,
                                                                                              region)
df_vci_smoothed, df_vci3m_smoothed = uf.load_smoothed_data(DATA_SOURCE, region, datasets)


shapefile_path = "./shapefiles/KEN_Adm2/KEN_Adm2.shp"
LEVEL_3_LABEL = "Adm2Name"


# ________________________________________
# Sub title forecast VCI3M
# ________________________________________
st.header("VCI3M Forecast", divider='gray')
st.write("Click on a sub county on the map below to view the VCI3M forecast")
col = st.columns(( 1, 1), gap='medium')
with col[0]:
    m = uf.create_base_map_kenya()

    shapefile = uf.add_VCI3M_to_shapefile(shapefile_path, LEVEL_3_LABEL, last_observed_VCI3M, datasets)

    bounds = [ 1, 10, 20, 35, 50, 100]

    #
    colormap = branca.colormap.LinearColormap(
        vmin=0,  # shapefile["VCI3M"].quantile(0.0),
        vmax=shapefile["VCI3M"].quantile(1),
        colors=[  "r", "orange", "green", "darkgreen"],
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

    # ________________________________________
    # Create map showing selected sub county
    # ________________________________________

    output = st_folium(m, width=700, height=500)


    if output['last_active_drawing']:
        selected_coulum = output["last_object_clicked_tooltip"].splitlines()[3].lstrip()

        # st.write(selected_coulum)
    else:
        selected_coulum = datasets[0]

with col[1]:
    # ________________________________________
    # Sub title forecast VCI3M
    # ________________________________________
    # st.subheader("Forecasted VCI3M", divider='gray')

    # ________________________________________
    # calculate errors from hindcasts for this subcounty
    # ________________________________________

    errors = uf.get_error(DATA_SOURCE, region,selected_coulum)


    df_forecasts_T = uf.load_forecasted_VCI3M(DATA_SOURCE, region)

    if selected_coulum ==  'Chereti/Weyib':
        dates_forecast = list(df_forecasts_T['Chereti-Weyib'].index)
        VCI3M_forecast = list(df_forecasts_T['Chereti-Weyib'].values)
        historical_smoothed_VCI3M = list(df_vci3m_smoothed['Chereti-Weyib'].values)
    else :

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



