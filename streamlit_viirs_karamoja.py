import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import h5py as h5
import datetime
import plot_map as get_map
import useful_functions as uf
# ________________________________________
# TITLE
# ________________________________________

# '''
# st.image("passage_logo_1_cluster_green_green.png",width = 150)
# # :earth_africa: VCI Monitoring & Forecasting
# A description can be placed here ....
# '''


colal, mid, colbe = st.columns([15,1,50])
with colal:
    st.image("passage_logo_1_cluster_green_green.png", width=140)
with colbe:
    st.header('VCI3M, NDVI Monitoring & Forecasting',divider='gray')

# st.divider()
# st.image("passage_logo_1_cluster_green_green.png",width = 100) #caption="Sunrise by the mountains"
# st.logo("passage_logo_1_cluster_green_green.png",)

# ________________________________________
# Select Cluster
# ________________________________________

# SELECT WHICH CLUSTER
DATA_SOURCE = "VIIRS"
# LEVEL_3_LABEL =""
clusters = ['CLUSTER_1', "CLUSTER_2", "CLUSTER_3"]

# Create columns
cola, colb,  = st.columns(2)

with cola:

    selected_cluster = st.selectbox("IGAD Cluster", clusters)



# ________________________________________
# LOAD SELECTED DATA
# ________________________________________

hdf_path = f"/Users/cg411/Documents/PASSAGE/projects/streamlit_vis/passage_clusters/{DATA_SOURCE}/{selected_cluster}/FinalSubCountyVCI_{selected_cluster}.h5"
hdf_file_viirs = h5.File(hdf_path, "r")

viirs_datasets = list(hdf_file_viirs.keys())

df = pd.DataFrame()
df_NDVI = pd.DataFrame()
last_observed_VCI3M = {}
for i, dataset in enumerate(viirs_datasets):
    final_subcounty_array_viirs = np.array(hdf_file_viirs[viirs_datasets[i]] , dtype=float)
    last_observed_VCI3M[dataset] = final_subcounty_array_viirs[-1, 3]
    df[dataset] = final_subcounty_array_viirs[:, 3]
    df_NDVI[dataset] = final_subcounty_array_viirs[:, 1]
    if i==0:
        time = final_subcounty_array_viirs[:, 0]
        dates = np.array([datetime.datetime(int(float(str(date)[:4])), 1, 1) + datetime.timedelta(
            int(float(str(date)[4:7])) - 1) if date > 0 else float("NaN") for date in time])
        min_date = dates[0]
        max_date = dates[-1]
        print(max_date)
        df = df.set_index(dates)
        df_NDVI = df_NDVI.set_index(dates)

# ________________________________________
# Select sub county
# ________________________________________

with colb:
    # SELECT SUBCOUNTY TO PRESENT
    selected_coulum = st.selectbox("County", df.columns)


col1, col2, col3 = st.columns(3)

if selected_cluster == "CLUSTER_1":
    shapefile_path = "/Users/cg411/Documents/PASSAGE/projects/astrocast_pipeline/shapefiles/IGAD_Cluster_123/IGAD_Cluster_1.shp"
    LEVEL_3_LABEL = "County"
elif selected_cluster == "CLUSTER_2":
    shapefile_path = "/Users/cg411/Documents/PASSAGE/projects/astrocast_pipeline/shapefiles/IGAD_Cluster_123/IGAD_Cluster_2.shp"
    LEVEL_3_LABEL = "WOREDANAME"
else:
    shapefile_path = "/Users/cg411/Documents/PASSAGE/projects/astrocast_pipeline/shapefiles/IGAD_Cluster_123/IGAD_Cluster_3.shp"
    LEVEL_3_LABEL ="DISTRICT"

# ________________________________________
# Create map showing selected sub county
# ________________________________________

fig, ax = get_map.create_map(selected_coulum ,shapefile_path,last_observed_VCI3M[selected_coulum],LEVEL_3_LABEL )

with col2:
    st.pyplot(fig, use_container_width=False)


# ________________________________________
# Sub title forecast VCI3M
# ________________________________________
st.subheader("Forecasted VCI3M", divider='gray')

# ________________________________________
# calculate errors from hindcasts for this subcounty
# ________________________________________
errors = uf.get_error(DATA_SOURCE,selected_cluster,selected_coulum)

df_forecasts = pd.read_excel(f"passage_clusters/{DATA_SOURCE}/{selected_cluster}/VCI3M_Overview_2024-09-01.xlsx") # HARDCODED!!!!!
df_forecasts_T = df_forecasts.set_index('Unnamed: 0').T

dates_forecast = list(df_forecasts_T[selected_coulum].index)
VCI3M_forecast = list(df_forecasts_T[selected_coulum].values)

VCI3M = list(df[selected_coulum].values)

# ________________________________________
# Create figures showing forecasted VCI3M
# ________________________________________
fig3, ax3 = uf.plot_forecasts(dates,VCI3M, dates_forecast,VCI3M_forecast, errors, max_date, selected_coulum)

st.pyplot(fig3)

# ________________________________________
# Subtitle
# ________________________________________

st.subheader("Historical VCI3M", divider='gray')

# ________________________________________
# Slider to select time period
# ________________________________________
from_date, to_date = st.slider(
    'Which time period are you interested in?',
    min_value= min_date,
    max_value= max_date,
    value=[min_date, max_date])


# Filter the data
filtered_df = df.loc[from_date:to_date]
filtered_df_NDVI = df_NDVI.loc[from_date:to_date]

# ________________________________________
# Create figures showing historical VCI3M
# ________________________________________

# streamlit line chart
st.line_chart(filtered_df[selected_coulum], x_label="Date", y_label="VCI3M")

# amtplotlib mine graph
fig2, ax2 = plt.subplots(figsize=(10, 7))
ax2 = filtered_df[selected_coulum].plot(color='black' )

ax2.set_ylim(0 , 100)
ax2.set_ylim(0, 120 )

ax2.set_xlabel("Time")
ax2.set_ylabel("VCI3M")

ax2.axhspan(0, 10, alpha=0.5, color="r")
ax2.axhspan(10, 20, alpha=0.5, color="darkorange")
ax2.axhspan(20, 35, alpha=0.5, color="yellow")
ax2.axhspan(35, 50, alpha=0.5, color="limegreen")
ax2.axhspan(50, 300, alpha=0.5, color="darkgreen")
st.pyplot(fig2)
# ________________________________________
# Display VCI3M dataframe
# ________________________________________
st.subheader("Historical weekly VCI3M dataframe for all regions ", divider='gray')
st.dataframe(filtered_df)

# ________________________________________
# Display historical NDVI
# ________________________________________
st.subheader("Historical weekly NDVI", divider='gray')
# streamlit line chart
st.line_chart(filtered_df_NDVI[selected_coulum], x_label="Date", y_label="NDVI")
