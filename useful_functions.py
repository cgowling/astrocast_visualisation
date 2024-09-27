import os
import numpy as np
import  h5py as h5
import matplotlib.pyplot as plt
from datetime import timedelta
import matplotlib.dates as mdates

DATA_SOURCE = "VIIRS"
LEVEL_1_NAME = "CLUSTER_1"


def get_error(DATA_SOURCE, LEVEL_1_NAME, dataset):
    errors = np.empty(11, dtype=float)

    hindcast_dir = os.path.join("passage_clusters",DATA_SOURCE,LEVEL_1_NAME,  f"hindcasts_{LEVEL_1_NAME}.h5")
    # if (hindcast_dir != ""):
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

def plot_forecasts(dates,VCI3M, dates_forecast,VCI3M_forecast, errors, last_date, dataset):
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.fill_between(
        dates_forecast[-11:],
        VCI3M_forecast[-11:] - errors,
        VCI3M_forecast[-11:] + errors,
        lw=3,
        label="Forecast VCI3M",
        color="blue",
        alpha=0.45,
        zorder=4,
        interpolate=True,
    )

    ax.plot(
        dates, VCI3M, linestyle="solid", lw=3, color="black", label=""
    )

    ax.plot(
        dates_forecast, VCI3M_forecast, linestyle="dashed", lw=3, color="black", label=""
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

    ax.set_title("VCI3M for {}".format(dataset), fontsize=20)

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


