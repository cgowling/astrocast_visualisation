# -*- coding: utf-8 -*-
"""This module creates the reports from the forecasts and saves as PDF

The class in this module is rather large and does not contain any calcualtions
,only the set up of the report. It has been made as clear as possible as this 
sort of thing in matplotlib is not ideal. If things are changed there can be a
butterfly effect very easily.

Created on Mon Nov 18 17:59:36 2019

@author: Andrew Bowell

"""
# Import the needed modules

import geopandas as gpd
import matplotlib
#matplotlib.use('agg')
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import numpy as np
import matplotlib as mp
import matplotlib.gridspec as gridspec
from datetime import timedelta
import h5py as h5
import os
import matplotlib.cbook as cbook
import matplotlib.dates as mdates
import shutil
import scipy.stats as stats

class createPDF:
    """Class housing the functions to set up the report
    
    Attributes
    ----------
    dataset : str 
        Name of dataset being looked at. This will become title for report and
        graphs in report.
    dataset_no : int
        The number of the dataset. This is so it can be looked up by comparing
        to the index of the shapefile.
    dates : :obj:`NumPy array` of :obj:`float`
        Dates of the known data and the forecast. Used for x-axis of plot and 
        the table as well. 
    VCI3M : :obj:`NumPy array` of :obj:`float`
        Known VCI3M as well as the forecast VCI3M.
    last_date : str
        Last date of which data was collected. This allows us to seperate the 
        forecast data from the known data.
    errors : :obj:`List` of :obj:`float` 
        Errors on the forecast at each week. Layout will change as these are
        just place holders at the moment.
    ax1 : Matplotlib Axis
        This is an axis instance from the module matplotlib. ax1 will be used 
        to plot the colorbar. 
    ax2 : Matplotlib Axis
        This is an axis instance from the module matplotlib. ax2 will be used 
        to plot the shapefile/map.
    ax3 : Matplotlib Axis
        This is an axis instance from the module matplotlib. ax3 will be used 
        to display the trend. (Bit useless. Fig text will be used in future 
       update)
    ax4 : Matplotlib Axis
        This is an axis instance from the module matplotlib. ax4 will be used 
        to plot the graph of the VCI3M time series. 
    ax5 : Matplotlib Axis
        This is an axis instance from the module matplotlib. ax5 will be used 
        to plot the table of VCI3M. 
    figure : Matplotlib Figure
        This is a matplotlib figure upon which axes can be placed.
    cmap : Matplotlib colourmap
        matplotlib colomap which can assign colours to different values or 
        different ranegs of values.
    norm : Matplotlib colourmap bounds 
        Uses the colormap to create the bounds. (min/max values)
    shapefile_path : str
        file path to the shapefile.
    database : str
        file path to the database file
    
    """ 
    def __init__(self,dataset,dataset_no,dates,predicted_VCI3M,last_known_date,
                 shapefile_path,database_path,column_name):
        """Initiate the attributes.

        Parameters
        ---------
        dataset : str 
           Name of dataset being looked at. This will become title for report 
           and graphs in report.
        dataset_no : int
           The number of the dataset. This is so it can be looked up by
           comparing to the index of the shapefile.
        dates : :obj:`NumPy array` of :obj:`float`
           Dates of the known data and the forecast. Used for x-axis of plot 
           and the table as well. 
        predicted_VCI3M : :obj:`NumPy array` of :obj:`float`
           Known VCI3M as well as the forecast VCI3M.
        last_known_date : str
           Last date of which data was collected. This allows us to seperate 
           the forecast data from the known data.
        database_path : str
            Databse name or file path so that errors can be read and calculated
            
        """
        self.dataset = dataset
        self.dataset_no = dataset_no
        self.dates = dates
        self.VCI3M = predicted_VCI3M
        self.last_date = last_known_date
        self.errors = np.empty(11,dtype=float)
        self.ax1,self.ax2,self.ax3,self.ax4,self.ax5 = None,None,None,None,None
        self.figure = None
        self.cmap = None
        self.norm = None
        self.shapefile_path = shapefile_path
        self.database = database_path
        self.column_name = column_name
        
        
    
    def forecast_store(self):
        
         file = self.database
         database_file = file[self.dataset.replace(' ','-')]
         for i in range(0,10):
             database_file[-10+i,4+i] = self.VCI3M[-10+i] 
                 
         #file.close()
        
    # Normal version of the function. Takes hindcasts from same file
    # def error_calc(self):
    #     """This function uses the hindcast data to calcualte the errors
        
    #     This function opens the main database file and compares the hindcast
    #     data for each lag time with the actual data. This is done by 
    #     calculating the residuals (actual-forecasted) for each prediction time
    #     step and then taking the standard deviation of the residuals. This is
    #     then multiplied by two so that 99% of future predictions will fall
    #     within our calculated uncertainty. 
        

    #     Returns
    #     -------
    #     None.

    #     """
    #     file = self.database
    #     print(self.dataset)
    #     dataset_array = np.array(file[self.dataset],dtype=float)
    #     dataset_array[dataset_array==0] = np.nan
    #     self.errors[0] = 0
        
    #     for jump_ahead in range(1,11):
    #         self.errors[jump_ahead] = np.nanstd(dataset_array[:,3]-
    #                                        dataset_array[:,jump_ahead+3])


        
            
    #     #file.close()
    #     self.set_up_figure()
    
        # Temp fcuntion - Takes precalculated hindcasts.
    def error_calc(self):
        """This function uses the hindcast data to calcualte the errors
        
        This function opens the main database file and compares the hindcast
        data for each lag time with the actual data. This is done by 
        calculating the residuals (actual-forecasted) for each prediction time
        step and then taking the standard deviation of the residuals. This is
        then multiplied by two so that 99% of future predictions will fall
        within our calculated uncertainty. 
        

        Returns
        -------
        None.

        """
        hindcast_file = h5.File(('FinalSubCountyVCI_hindcasts.h5'), 'r')
        print(self.dataset)
        dataset_array = np.array(hindcast_file[self.dataset], dtype=float)
        dataset_array[dataset_array==0] = np.nan
        self.errors[0] = 0
        
        for jump_ahead in range(1,11):
            self.errors[jump_ahead] = np.nanstd(dataset_array[:,3]-
                                           dataset_array[:,jump_ahead+3])


        
            
        #file.close()
        self.set_up_figure()
        
        
        
    def set_up_figure(self):
        """This function creates the figure and axes.
        
        Matplotlib's gridspec function is used to assin different parts of the
        figure to different parts of the report. The axis is turned of for 
        some of the axes like the map so there is not a square box around it.
        The title of the figure is also set as well as adding some text about 
        where the forecasts can currently be found. The colour_bar and 
        create_map functions are then called.
    
        Returns
        -------
        None.

        """
        # TEMP COMMENETED OUT WHILE PREVIOUS HINDCASTS USED
        #self.forecast_store()
        self.figure = plt.figure(figsize=(11.69*2,8.27*2))
        
        layout = gridspec.GridSpec(ncols=141, nrows=100, figure=self.figure)
        
        self.ax1 = self.figure.add_subplot(layout[5:8, 0:60])
        
        self.ax2 = self.figure.add_subplot(layout[0:, 0:60])
        
        self.ax3 = self.figure.add_subplot(layout[6:18, 0:])
        
        self.ax4 = self.figure.add_subplot(layout[5:45,65:])
        
        self.ax5 = self.figure.add_subplot(layout[60:80,1:20])
        
        self.ax2.axis('off')
        self.ax3.axis('off')
        self.ax5.axis('off')
        
        plt.subplots_adjust(hspace = -.175)
        plt.subplots_adjust(wspace = +1.5)
        
        shapefile = gpd.read_file(self.shapefile_path)
                
        shapefile = shapefile.loc[shapefile[self.column_name] ==\
                                    self.dataset.replace('-', ' ')]
        
        main_county = str(shapefile['Adm1Name'].values[0])
        print(main_county)
        
        # self.figure.suptitle(str(self.dataset)+" Vegetation Outlook",
        #                      fontsize=24)
        
        self.figure.suptitle('{}, {} County Vegetation Outlook'.format(self.dataset,main_county),
                             fontsize=24,x=0.535)
        
        self.figure.subplots_adjust(top=0.95)
    
        self.figure.patch.set_facecolor('lightblue')
        
        img = plt.imread('AC_logo.png')
        self.ax5.imshow(img)
        
        
        
        self.figure.text(0.577,0.26, ("Please find our weekly forecasts at the " 
                               "link below \n \n"
                               "       https://tinyurl.com/AstroCastForecasts")
                               ,fontsize=18)
        
        plt.subplots_adjust(left=0.15, bottom=0.005, right=0.93, top=0.95, 
                        wspace=0, hspace=0)
        
        self.colour_bar()
        self.create_map()
    
    def colour_bar(self):
        """ This function creates the colourbar
        
        The bounds of the colourbar are set along with the colours. The colour
        bar is then added onto ax1 as well as sorting out the tick frequency.
        The title of the colourbar is also set.

        Returns
        -------
        None.

        """
        
        bounds = [0,0.00001, 10, 20, 35,50,100]
        self.cmap = mp.colors.ListedColormap(['white','r', 'darkorange',
                                              'yellow','limegreen',
                                              'darkgreen'])
        
        self.norm = mp.colors.BoundaryNorm(bounds, self.cmap.N)
        
        mp.colorbar.ColorbarBase(ax=self.ax1, cmap=self.cmap,norm=self.norm,
                                 orientation='horizontal')



    
        # self.ax1.set_title('VCI3M Forecast For ' +
        #                    str(self.dates[-7].date()),fontsize=20)

        self.ax1.set_title('VCI3M forecast for {}'.format(self.dates[-5].strftime('%d/%m/%Y')),
                           fontsize=20)


        self.ax1.tick_params(labelsize=16)
        
        labels = [tick.get_text() for tick in self.ax1.get_xticklabels()]
        labels[0] = 'No Data'
        self.ax1.set_xticklabels(labels)

        
    def create_map(self):
        """This function plots the map of a shapefile using geopandas.
        
        Using geopandas the shapefile is read and a new column of VCI3M is 
        added onto it. Everything is set to zero apart from the dataset we are
        creating the report for. The shapefile is then plotted based on it's
        VCI3M. The set_trend function is then called.

        Returns
        -------
        None.

        """
        
        shapefile = gpd.read_file(self.shapefile_path)

        map_VCI3M = np.full(len(shapefile),0)
        
        map_VCI3M[int(list(shapefile.loc[shapefile[self.column_name] ==\
                                    self.dataset.replace('-', ' ')].index)[0])] = self.VCI3M[-5]
        
        shapefile['VCI3M'] = map_VCI3M
        
        self.ax2 = shapefile.plot(ax=self.ax2,column ='VCI3M',cmap = self.cmap,
                                  norm=self.norm,legend= False,
                                  edgecolor='Black',
                                  label= shapefile[self.column_name])
        
        old_pos = self.ax2.get_position()
        
        new_pos = [old_pos.x0, old_pos.y0 + 0.08,  old_pos.width, old_pos.height] 

        self.ax2.set_position(new_pos)
        
        self.set_trend()



    def set_trend(self):
        """ This function sets the trend for the VCI3M
        
        The trend will simply be up or down. It just checks if the VCI3M value
        in a few weeks will be larger than that in a couple of weeks. The text 
        is then displayed to ax3

        Returns
        -------
        None.

        """
            
        if self.VCI3M[-6] > self.VCI3M[-7]:
            self.ax3.text(0.277,0.45,'Trend = Up',verticalalignment='center',
                          horizontalalignment='right',
                          transform=self.ax3.transAxes, fontsize=22)
        else:
            self.ax3.text(0.277,0.45,'Trend = Down',verticalalignment='center',
                          horizontalalignment='right',
                          transform=self.ax3.transAxes,fontsize=22)
            
        self.VCI3M_graph()    

    def VCI3M_graph(self):
        """This function handles the grpahing of the time series.
        
        The matplotlib fill between function allows a shaded region to be 
        created where there is uncertainty. We know that the predicted VCI3M 
        will just be the last 9 values so this is easy enough. The whole time
        series is then plotted as a solid black line and then a black, vertical
        dashed line is used to signify the last known date data was collected
        on. As currently, the data is quite noisey the VCI3M can dip below 
        0. There is a small if statement that checks for this and then changes
        the limits on the plot so that all the data can be seen. The background
        is then shaded in using the colourmap created earlier.
        This is all plotted to ax4.
    
        Returns
        -------
        None.

        """
        #------------------- VCI3M Graph -----------------------#
            
        # The 4th axis plots the past 30 weeks of actual data and then the 
        #predicted data is also plotted
        # The data then has the error shaded onto it. 

        self.ax4.fill_between(self.dates[-11:], self.VCI3M[-11:]-self.errors,
                              self.VCI3M[-11:] + self.errors,lw=3,
                              label='Forecast VCI3M',color='blue',
                              alpha=0.45,zorder=4,interpolate=True)
        
        
      
        
        self.ax4.plot(self.dates,self.VCI3M, linestyle = 'solid' ,
                      lw = 3, color = 'black',label='')
        
        self.ax4.vlines(self.last_date,-100,300,linestyle = '--',color = 'black',
                        lw = 3, label = 'Day of last observation')
        
    
        self.ax4.set_xlim(self.dates[-40],self.dates[-1]+timedelta(days=7))
        
        max_value,min_value =np.max(self.VCI3M[-40:]), np.min(self.VCI3M[-40:])
                                                              
        if min_value < 0 :
            self.ax4.set_ylim(min_value-10,100)
        
            self.ax4.axhspan(-100, 10, alpha=0.5, color='r')
        else:
            self.ax4.set_ylim(0,100)
            self.ax4.axhspan(0, 10, alpha=0.5, color='r')
            
        if max_value > 100:
            self.ax4.set_ylim(0,max_value+5)
        
        # Shading the background based on where the VCI3M is
        
        
        self.ax4.axhspan(10, 20, alpha=0.5, color='darkorange')
        self.ax4.axhspan(20, 35, alpha=0.5, color='yellow')
        self.ax4.axhspan(35, 50, alpha=0.5, color='limegreen')
        self.ax4.axhspan(50, 300, alpha=0.5, color='darkgreen')

        
        self.ax4.set_title('VCI3M for {}'.format(self.dataset),fontsize=20)
        
        #self.ax4.set_title(str(self.dataset) + ' VCI3M',fontsize=20)
        
        self.ax4.legend()
        #self.figure.autofmt_xdate()

        # use a more precise date string for the x axis locations in the
        # toolbar
        fmt_xdata = mdates.DateFormatter('%d/%m/%y')
        self.ax4.tick_params(axis='x', labelsize=13)
        self.ax4.tick_params(axis='y', labelsize=12)
        self.ax4.xaxis.set_major_formatter(fmt_xdata)
        self.table()


    def table(self):
        """Small function creating the table for the report.
            
        A table is created with the dates and corresponding VCI3M predicted 
        values. The background is set to be the same colours as the cmap 
        created earlier. This is also plotted to ax4 as tables need to be
        accompanied by graphs when using matplotlib.
        
        Returns
        -------
        None.
        
        """
        
        Date_labels = [date.strftime('%d/%m/%y') for date in self.dates[-11:]]
        
        Date_labels[0] = str('Last known\nVCI value\n\n')+ Date_labels[0] 
        
        
        TableList = np.round(self.VCI3M[-11:],1)
        
        #~~~~~~~~~~~~~~~~~~ Calc error table ~~~~~~~~~~~~~~~~~~~~~~~~#
        
        x1_lims = [np.inf,50,35,20,10]
        x2_lims = [50,35,20,10,-np.inf]
        
        error_table_store = np.empty((len(x1_lims)+1,(len(TableList))))

        for week_counter,(mean,sd) in enumerate(zip(TableList,self.errors)):
            for lim_counter,(x1,x2) in enumerate(zip(x1_lims,x2_lims)):
                prob1=stats.norm.cdf((x1-mean)/sd)
                prob2=stats.norm.cdf((x2-mean)/sd)

                error_table_store[lim_counter+1,week_counter] = np.round((prob1-prob2)*100,1)
                
        error_table_store[0,:] = TableList
        


        RowLabels = ['VCI3M','\u2265 50','35-49','21-34','10-20','< 10']
        RowLabels = ['VCI3M','Likelihood','forecast','is in','catergory','(%)']
        TheTable = self.ax4.table(cellText=error_table_store,
                  colLabels = Date_labels,
                      rowLabels =RowLabels,bbox=[0.0,-0.5,1,.43],fontsize=40,
                      cellLoc='center',rowLoc='center',
                          cellColours=self.cmap(self.norm(error_table_store)))
        
        
        
        # the_table[(1, 0)].set_facecolor("#56b5fd")
        # the_table[(2, 0)].set_facecolor("#1ac3f5")

    
        #[0.0,-0.5,1,.28]
        TheTable.auto_set_font_size(False)
        #TheTable.set_fontsize(10.5)
        #TheTable.scale(2, 1)
        for cell in TheTable._cells:

            if cell[0] == 0:
                TheTable._cells[cell].set_fontsize(11.8)
                TheTable._cells[cell].set_height(.2)
                if cell[1] == 0:
                    TheTable._cells[cell].set_fontsize(11)
            


            if cell[0] == 1:
                TheTable._cells[cell].set_fontsize(14)
                TheTable._cells[cell].set_height(.13)
            
            if cell[0] > 1:
                TheTable._cells[cell].set_height(.07)
                #
            if cell[0] == 2 and cell[1] >= 0:
                TheTable._cells[cell].set_facecolor("darkgreen")
            if cell[0] == 3 and cell[1] >= 0:
                TheTable._cells[cell].set_facecolor("limegreen")    
            if cell[0] == 4 and cell[1] >= 0:
                TheTable._cells[cell].set_facecolor("yellow")    
            if cell[0] == 5 and cell[1] >= 0:
                TheTable._cells[cell].set_facecolor("darkorange")    
            if cell[0] == 6 and cell[1] >= 0:
                TheTable._cells[cell].set_facecolor("r")       
            if cell[1] == -1 and (cell[0] >= 2 and cell[0] <= 5):
                #TheTable._cells[cell].set_facecolor('white')
                TheTable._cells[cell].visible_edges = 'RL'
                
            if cell[1] == -1 and (cell[0] ==6):
                #TheTable._cells[cell].set_facecolor('white')
                TheTable._cells[cell].visible_edges = 'BL'

        self.ax4.axvline(x=20, ymin=0.25, ymax=100,ls='--')
        
        self.save_show_fig()
        
    def save_show_fig(self):
        """Small function that saves the figure.
        
        Save the figure with the name of the dataset and the data which the
        data was last measured on. Also show the figure,

        Returns
        -------
        None.

        """
        path = 'Forecasts/PDF Reports/'+str(self.dates[-11].date())
        
        if not os.path.exists(path):
            os.mkdir(path)
        
        plt.savefig('Forecasts/PDF Reports/'+str(self.dates[-11].date())+'/Forecast for '+str(self.dataset)+' dated ' +
                   str(self.dates[-11].date())+'.pdf',dpi = 400,
                       facecolor=self.figure.get_facecolor(),bbox_inches ='tight',
                       pad_inches=0.23)
       
        plt.show()





    
    
    
    
    
    
    
