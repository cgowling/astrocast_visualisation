import os
import numpy as np
import  h5py as h5
import matplotlib.pyplot as plt
from datetime import timedelta
import matplotlib.dates as mdates
import streamlit as st
import pandas as pd
import datetime
import geopandas as gpd
import folium
DATA_SOURCE = "VIIRS"
LEVEL_1_NAME = "CLUSTER_1"

# import sys
# sys.path.append('./shapefiles')


def plot_forecasts(dates,VCI3M, dates_forecast,VCI3M_forecast, errors, last_date, dataset, LEVEL_2_NAME= ""):
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.fill_between(
        dates_forecast[-11:],
        VCI3M_forecast[-11:] - errors,
        VCI3M_forecast[-11:] + errors,
        lw=3,
        label="Forecast VCI3M uncertainty",
        color="blue",
        alpha=0.45,
        zorder=4,
        interpolate=True,
    )

    ax.plot(
        dates, VCI3M, linestyle="solid", lw=3, color="black", label=""
    )

    ax.plot(
        dates_forecast, VCI3M_forecast, linestyle="dotted", lw=3, color="black", label="Forecast VCI3M"
    )

    ax.vlines(
        last_date,
        -100,
        300,
        linestyle="--",
        color="black",
        lw=3,
        label="Day of last observation",
    )

    ax.set_xlim(dates[-35], dates_forecast[-1] + timedelta(days=7))

    max_value, min_value = np.max(VCI3M[-40:]), np.min(VCI3M[-40:])

    if min_value < 0:
        ax.set_ylim(min_value - 10, 100)

        ax.axhspan(-100, 10, alpha=0.5, color="r")
    else:
        ax.set_ylim(0, 100)
        ax.axhspan(0, 10, alpha=0.5, color="r")

    if max_value > 100:
        ax.set_ylim(0, max_value + 5)

    # Shading the background based on where the VCI3M is

    ax.axhspan(10, 20, alpha=0.5, color="darkorange")
    ax.axhspan(20, 35, alpha=0.5, color="yellow")
    ax.axhspan(35, 50, alpha=0.5, color="limegreen")
    ax.axhspan(50, 300, alpha=0.5, color="darkgreen")

    ax.set_title("VCI3M for {} {}".format(dataset, LEVEL_2_NAME), fontsize=20)

    # self.ax4.set_title(str(self.dataset) + ' VCI3M',fontsize=20)

    ax.legend()
    # self.figure.autofmt_xdate()

    # use a more precise date string for the x axis locations in the
    # toolbar
    fmt_xdata = mdates.DateFormatter("%d/%m/%y")
    ax.tick_params(axis="x", labelsize=13)
    ax.tick_params(axis="y", labelsize=12)
    ax.xaxis.set_major_formatter(fmt_xdata)
    return fig, ax




@st.cache_data
def load_observed_data(DATA_SOURCE,selected_cluster):

    hdf_path = f"./passage_clusters/{DATA_SOURCE}/{selected_cluster}/FinalSubCountyVCI_{selected_cluster}.h5"
    hdf_file = h5.File(hdf_path, "r")

    if selected_cluster == "Kenya":
        NDMA_pilot_counties  = ["Garissa", "Kilifi", "Makueni", "Mandera", "Marsabit", "Taita Taveta", "Turkana", "Wajir",
                          "West Pokot"]
        # mask = shapefile["Adm1Name"].isin(LEVEL_2_LABELs)
        # filter_test = shapefile[mask]
        # test_list = filter_test["Adm2Name"].to_list()
        # NDMA_pilot_sub_counties
        datasets = ['Voi', 'Mwatate', 'Wundanyi', 'Taveta', 'Rabai', 'Kilifi South', 'Kaloleni', 'Magarini', 'Malindi', 'Kilifi North',
                                   'Ganze', 'Laisamis', 'Moyale', 'North Horr', 'Saku', 'Lafey', 'Mandera North', 'Banissa', 'Mandera West', 'Mandera South',
                                   'Mandera East', 'Tarbaj', 'Wajir North', 'Wajir South', 'Wajir West', 'Balambala', 'Dujis', 'Ijara', 'Fafi', 'Lagdera', 'Dadaab',
                                   'Eldas', 'Wajir East', 'Kacheliba', 'Pokot South', 'Sigor', 'Kapenguria', 'Turkana East', 'Turkana South', 'Loima', 'Turkana Central',
                                   'Turkana West', 'Turkana North', 'Kibwezi East', 'Kibwezi West', 'Makueni', 'Kaiti', 'Kilome', 'Mbooni']

        # datasets = ["Eldas", "Kieni", "Kitui Central", "Kitui East", "Kitui Rural", "Kitui South", "Kitui West",
        #                "Laisamis", "Loima", "Mathira", "Moyale", "Mukurweni", "Mwatate", "Mwingi East",
        #                "Mwingi North", "Mwingi West", "North Horr", "Nyeri Town", "Othaya", "Saku", "Samburu East",
        #                "Samburu North", "Samburu West", "Tarbaj", "Taveta", "Tetu", "Turkana Central",
        #                "Turkana East", "Turkana North", "Turkana South", "Turkana West", "Voi", "Wajir East",
        #                "Wajir North", "Wajir South", "Wajir West", "Wundanyi"]
    else :
        datasets = list(hdf_file.keys())





    df = pd.DataFrame()
    df_NDVI = pd.DataFrame()
    last_observed_VCI3M = {}
    for i, dataset in enumerate(datasets):
        final_subcounty_array = np.array(hdf_file[datasets[i]] , dtype=float)
        last_observed_VCI3M[dataset] = final_subcounty_array[-1, 3]
        df[dataset] = final_subcounty_array[12:, 3]
        df_NDVI[dataset] = final_subcounty_array[12:, 1]
        if i==0:
            time = final_subcounty_array[12:, 0]
            dates = np.array([datetime.datetime(int(float(str(date)[:4])), 1, 1) + datetime.timedelta(
                int(float(str(date)[4:7])) - 1) if date > 0 else float("NaN") for date in time])
            min_date = dates[0]
            max_date = dates[-1]
            # print(max_date)
            df["Date"] = dates
            df = df.set_index("Date")
            df_NDVI["Date"] = dates
            df_NDVI =  df_NDVI.set_index("Date")
    return datasets, df, df_NDVI, last_observed_VCI3M,  min_date , max_date, dates



@st.cache_data
def load_smoothed_data(DATA_SOURCE, selected_cluster, datasets):

    hdf_path_smoothed_VCI3M = f"./passage_clusters/{DATA_SOURCE}/{selected_cluster}/smoothed_historical_VCI_{selected_cluster}.h5"
    hdf_file_smoothed_VCI3M = h5.File(hdf_path_smoothed_VCI3M, "r")
    # smoothed_datasets = list(hdf_file_smoothed_VCI3M.keys())
    df_vci_smoothed = pd.DataFrame()
    df_vci3m_smoothed =  pd.DataFrame()
    for i, dataset in enumerate(datasets):
        final_VCI_array = np.array(hdf_file_smoothed_VCI3M[datasets[i]], dtype=float)

        df_vci_smoothed[dataset] = final_VCI_array[12:, 1]
        df_vci3m_smoothed[dataset] = final_VCI_array[12:, 2]
        if i==0:
            time = final_VCI_array[12:, 0]
            dates = np.array([datetime.datetime(int(float(str(date)[:4])), 1, 1) + datetime.timedelta(
                int(float(str(date)[4:7])) - 1) if date > 0 else float("NaN") for date in time])
            min_date = dates[0]
            max_date = dates[-1]
            # print(max_date)
            df_vci_smoothed["Date"] = dates
            df_vci_smoothed = df_vci_smoothed.set_index("Date")
            df_vci3m_smoothed = df_vci3m_smoothed.set_index(dates)

    return df_vci_smoothed, df_vci3m_smoothed


@st.cache_data
def load_forecasted_VCI3M(DATA_SOURCE, selected_cluster):
    df_forecasts = pd.read_excel(
        f"./passage_clusters/{DATA_SOURCE}/{selected_cluster}/VCI3M_Forecast_Overview_{selected_cluster}.xlsx")  # HARDCODED!!!!!
    df_forecasts_T = df_forecasts.set_index('Unnamed: 0').T

    return df_forecasts_T


@st.cache_data
def add_VCI3M_to_shapefile(shapefile_path, LEVEL_3_LABEL,VCI3M, datasets):

    shapefile = gpd.read_file(shapefile_path)

    map_VCI3M = np.full(len(shapefile), 0)


    for i, dataset in enumerate(datasets):
        map_VCI3M[
                int(
                    list(
                        shapefile.loc[
                            shapefile[LEVEL_3_LABEL] == dataset.replace("-", "/")
                            ].index
                    )[0]
                )
            ] = VCI3M[dataset]


    shapefile["VCI3M"] = map_VCI3M
    return shapefile


@st.cache_data
def add_NDVI_to_shapefile(shapefile_path, LEVEL_3_LABEL,NDVI, datasets):

    shapefile = gpd.read_file(shapefile_path)

    map_NDVI = np.full(len(shapefile), 1.1)


    for i, dataset in enumerate(datasets):
        map_NDVI[
                int(
                    list(
                        shapefile.loc[
                            shapefile[LEVEL_3_LABEL] == dataset.replace("-", "/")
                            ].index
                    )[0]
                )
            ] = NDVI[dataset]


    shapefile["NDVI"] = map_NDVI
    return shapefile

@st.cache_data
def get_error(DATA_SOURCE, LEVEL_1_NAME, dataset):
    errors = np.empty(11, dtype=float)

    hindcast_dir = os.path.join("passage_clusters",DATA_SOURCE,LEVEL_1_NAME,  f"hindcasts_{LEVEL_1_NAME}.h5")
    # if (hindcast_dir != ""):@st.cache_data
    #     hindcast_dir = os.path.join(hindcast_dir, f"hindcasts_{LEVEL_1_NAME}.h5")
    # else:
    #     hindcast_dir = f"hindcasts_{LEVEL_1_NAME}.h5"
    # print(f"Opening Hindcast file {hindcast_dir}")
    hindcast_file = h5.File((hindcast_dir), "r")
    # print(self.dataset)
    dataset_array = np.array(hindcast_file[dataset], dtype=float)
    dataset_array[dataset_array == 0] = np.nan
    errors[0] = 0

    for jump_ahead in range(1, 11):
        errors[jump_ahead] = np.nanstd(
            dataset_array[:, 3] - dataset_array[:, jump_ahead + 3]
        )
    return errors


@st.cache_data
def create_base_map_passage_clusters():

    m = folium.Map(location=(3.162455530237848, 37.61718750000001), zoom_start=6.2, tiles="cartodb positron")

    shapefile_path_cluster_1 = "./shapefiles/IGAD_Cluster_123/IGAD_Cluster_1.shp"
    LEVEL_3_LABEL_cluster_1 = "County"

    shapefile_path_cluster_2 = "./shapefiles/IGAD_Cluster_123/IGAD_Cluster_2.shp"
    LEVEL_3_LABEL_cluster_2 = "WOREDANAME"

    shapefile_path_cluster_3 = "./shapefiles/IGAD_Cluster_123/IGAD_Cluster_3.shp"
    LEVEL_3_LABEL_cluster_3 = "DISTRICT"

    shapefile_paths = [shapefile_path_cluster_1,shapefile_path_cluster_2, shapefile_path_cluster_3]

    level_3_labels = [LEVEL_3_LABEL_cluster_1,LEVEL_3_LABEL_cluster_2,LEVEL_3_LABEL_cluster_3]
    for i, shapefile_p in enumerate(shapefile_paths):
        level_3_label = level_3_labels[i]
        shapefile = gpd.read_file(shapefile_p)
        shapefile = shapefile.to_crs(epsg=4326)
        for _, r in shapefile.iterrows():
            # Without simplifying the representation of each borough,
            # the map might not be displayed
            sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001)
            geo_j = sim_geo.to_json()
            geo_j = folium.GeoJson(data=geo_j)# , style_function=lambda x: {"fillColor": colour}
            folium.Popup(r[level_3_label]).add_to(geo_j)
            geo_j.add_to(m)
    return m




@st.cache_data
def create_base_map_kenya():

    m = folium.Map(location=(0.4048951780498096, 37.67519396600542), zoom_start=6.2, tiles="cartodb positron")
    shapefile_path = "./shapefiles/KEN_Adm2/KEN_Adm2.shp"
    LEVEL_3_LABEL = "Adm2Name"


    level_3_label = LEVEL_3_LABEL
    shapefile = gpd.read_file(shapefile_path)
    shapefile = shapefile.to_crs(epsg=4326)
    for _, r in shapefile.iterrows():
        # Without simplifying the representation of each borough,
        # the map might not be displayed
        sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j)# , style_function=lambda x: {"fillColor": colour}
        folium.Popup(r[level_3_label]).add_to(geo_j)
        geo_j.add_to(m)
    return m



# DATA_SOURCE = "VIIRS"
# region = "Kenya"
#
# datasets, df, df_NDVI, last_observed_VCI3M, min_date, max_date, dates = load_observed_data(DATA_SOURCE,
#                                                                                               region)
#
