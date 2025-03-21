import streamlit as st
import streamlit as st
import time
import numpy as np
import useful_functions as uf
from streamlit_folium import st_folium

import streamlit as st
import matplotlib.gridspec as gridspec
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
import matplotlib as mp

# import sys
# sys.path.append('./../')

def convert_julian_doy_to_datetime(date):
    return datetime.datetime(int(str(date)[:4]), 1, 1) + datetime.timedelta(
        int(str(date)[4:7]) - 1)


def plot_NDVI_shapefile_map(shapefile, LEVEL_3_LABEL):
    fig, ax = plt.subplots(figsize=(3, 3))
    fig.patch.set_facecolor("lightblue")

    ax = shapefile.plot(
        ax=ax,
        column="NDVI",
        cmap=cmap,
        norm=norm,
        legend=False,
        edgecolor="Black",
        linewidth=0.3,
        label=shapefile[LEVEL_3_LABEL],
    )

    ax.axis("off")
    plt.tight_layout()
    return fig, ax


DATA_SOURCE = "VIIRS"
region = "Kenya"

bounds = [-1.0, -0.2, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]

# Define the HTML color codes corresponding to each range
colors = [
    "#000000",  # NDVI < -0.2
    "#a50026",  # -0.2 <= NDVI < 0
    "#d73027",  # 0 <= NDVI < 0.1
    "#f46d43",  # 0.1 <= NDVI < 0.2
    "#fdae61",  # 0.2 <= NDVI < 0.3
    "#fee08b",  # 0.3 <= NDVI < 0.4
    "#ffffbf",  # 0.4 <= NDVI < 0.5
    "#d9ef8b",  # 0.5 <= NDVI < 0.6
    "#a6d96a",  # 0.6 <= NDVI < 0.7
    "#66bd63",  # 0.7 <= NDVI < 0.8
    "#1a9850",  # 0.8 <= NDVI < 0.9
    "#006837",  # 0.9 <= NDVI <= 1.0,
    "#FFFFFF"  # NDVI > 1.0 fill value ,
]
cmap = mp.colors.ListedColormap(colors)

norm = mp.colors.BoundaryNorm(bounds,cmap.N)

st.set_page_config(
    page_title="Kenya vegetation condition, NDMA pilot ",
    layout="wide",
    initial_sidebar_state="expanded")


st.header("NDVI monitoring ", divider='gray')


datasets, df, df_NDVI, last_observed_VCI3M, min_date, max_date, dates = uf.load_observed_data(DATA_SOURCE,
                                                                                              region)

NDMA_pilot_counties = ["Garissa", "Kilifi", "Makueni", "Mandera", "Marsabit", "Taita Taveta", "Turkana", "Wajir",
                       "West Pokot"]
selected_pilot_county = st.selectbox("County NDVI",(NDMA_pilot_counties))

shapefile_path = "shapefiles/KEN_Adm2/KEN_Adm2.shp"
LEVEL_2_LABEL = "Adm1Name"
LEVEL_3_LABEL = "Adm2Name"
shapefile_raw = gpd.read_file(shapefile_path)
shapefile_filtered = shapefile_raw.loc[(shapefile_raw[LEVEL_2_LABEL]==selected_pilot_county) ]


filtered_datasets = shapefile_filtered [LEVEL_3_LABEL].tolist()


path_to_pilot_county_jpegs = f"./passage_clusters/VIIRS/Kenya/NDVI_images/{selected_pilot_county}/"

jpg_files = sorted(glob.glob(path_to_pilot_county_jpegs + "*.jpeg"))
dates = [convert_julian_doy_to_datetime(x.split(f"{selected_pilot_county}_")[1][:7]).date().strftime("%Y-%m-%d") for x in jpg_files]

jpg_date = st.select_slider(f"Move the slider to view the last 12 weeks of NDVI observations for {selected_pilot_county}" , options=dates[-12:], value=dates[-1])
# print(jpg_date)
# print(df_NDVI.loc[jpg_date])#.loc[jpg_date]


selected_jpeg = jpg_files[dates.index(jpg_date)]
# print(selected_jpeg)
selected_NDVI = df_NDVI.loc[jpg_date]


st.subheader(f"NDVI for week ending {jpg_date} ")

col_ndvi_monitoring  = st.columns(( 1, 1,0.5), gap='medium')

with col_ndvi_monitoring[0]:

    st.write("VIIRS data at 500m resolution")
    st.image(selected_jpeg)#, caption="NDVI"

with col_ndvi_monitoring[1]:
    st.write(f"NDVI aggregated to mean sub-scounty for week ending {jpg_date}")
    shapefile = uf.add_NDVI_to_shapefile(shapefile_path, LEVEL_3_LABEL, selected_NDVI, filtered_datasets)

    fig, ax = plot_NDVI_shapefile_map(shapefile, LEVEL_3_LABEL)

    st.pyplot(fig)

with col_ndvi_monitoring[2]:
    st.write(f"NDVI colour reference")
    figure = plt.figure(figsize=(1, 4))
    figure.patch.set_facecolor("lightblue")
    # layout = gridspec.GridSpec(ncols=50, nrows=100, figure=figure)
    ax1 = figure.add_subplot()  # colorbar

    mp.colorbar.ColorbarBase(ax=ax1, cmap=cmap, norm=norm, orientation="vertical")
    # ax1.set_title("NDVI values", fontsize=20 )
    ax1.tick_params(labelsize=16)
    labels = [tick.get_text() for tick in ax1.get_xticklabels()]

    st.pyplot(figure)

