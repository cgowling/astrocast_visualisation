import geopandas as gpd
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
# from matplotlib_scalebar.scalebar import ScaleBar

bounds = [0, 0.00001, 10, 20, 35, 50, 100]
cmap = mp.colors.ListedColormap(
    ["white", "r", "darkorange", "yellow", "limegreen", "darkgreen"]
)

norm = mp.colors.BoundaryNorm(bounds,cmap.N)
def create_map(dataset,shapefile_path, VCI3M,LEVEL_3_LABEL ):
    fig, ax = plt.subplots(figsize=(2, 2))
    fig.patch.set_facecolor("lightblue")

    """This function plots the map of a shapefile using geopandas.

    Using geopandas the shapefile is read and a new column of VCI3M is
    added onto it. Everything is set to zero apart from the dataset we are
    creating the report for. The shapefile is then plotted based on it's
    VCI3M. 

    Returns
    -------
    fig,ax.

    """
    # print("Creating map...")

    shapefile = gpd.read_file(shapefile_path)
    # shapefile =     shapefile.to_crs(32619)
    map_VCI3M = np.full(len(shapefile), 0)

    map_VCI3M[
        int(
            list(
                shapefile.loc[
                    shapefile[LEVEL_3_LABEL] == dataset.replace("-", "/")
                    ].index
            )[0]
        )
    ] = VCI3M

    shapefile["VCI3M"] = map_VCI3M

    ax = shapefile.plot(
        ax= ax,
        column="VCI3M",
        cmap=cmap,
        norm=norm,
        legend=False,
        edgecolor="Black",
        label=shapefile[LEVEL_3_LABEL],
    )
    # scale = ScaleBar(dx=1, box_alpha=0.7,location="lower left")

    # ax.add_artist(scale)
    ax.axis("off")
    return fig, ax

