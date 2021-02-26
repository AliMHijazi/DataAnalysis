import os
import csv
import numpy as np
import pandas
import glob
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from numpy import genfromtxt
from datetime import datetime
from shutil import copyfile

filename = os.path.realpath(__file__)                   # Current file name
dirname = os.path.dirname(os.path.realpath(__file__))   # Directory of this file
datalocation = dirname + "/Data"                        # Location where data will be savednh
				
#-----------------------------------------------------#

def main(datalocation): 
    gatherDeathData(datalocation)

#-----------------------------------------------------#

def gatherDeathData(datalocation):
    locationsdeathdata = []
    locationcount = 0
    anotherlocation = "y"
    locationlist = []

    aspercentage = input("Plot as a percentage of population (y/n)? [Enter = n]: ")	# Plot as a % of pop. or total deaths.
    if aspercentage == "":
        aspercentage = "no"
    while(anotherlocation.lower() != "no" and anotherlocation.lower() != "n"):		# Collects and downloads (if needed) as many
        dontdownload = 0
        exist = "y"									# locations as requested.
        parishcounty = input("Parish/County (press enter for entire state): ")
        state = input("State: ")
        if parishcounty == "":
            locationofinterest = state
        else:
            locationofinterest = f'{parishcounty}_{state}'
        try:
            locationsdeathdata.append(pandas.read_csv(datalocation + "/" + locationofinterest + "_Deaths.csv"))
        except Exception as e:
            downloaddata = input(f"{locationofinterest}_Deaths.csv does not exist. Download? (y/n): ").lower()
            exist = "n"
            if downloaddata.lower() == "y" or downloaddata.lower() == "yes":
                collectDeathData(parishcounty, state, datalocation)
                locationsdeathdata.append(pandas.read_csv(datalocation + "/" + locationofinterest + "_Deaths.csv"))
            else:
                dontdownload = 1
        if exist == "y":
            print(f"{locationofinterest}_Deaths.csv exists.")
            print("The most recent file is: " + 
                  os.path.basename(max(glob.glob(datalocation +
                                                 "/" + 
                                                 locationofinterest + 
                                                 "_Deaths_*.csv"), 
                                                 key=os.path.getctime)))
            newdata = input("Download new data? (y/n): ").lower()
            if newdata.lower() == "y" or newdata.lower() == "yes":
                collectDeathData(parishcounty, state, datalocation)
                locationsdeathdata[locationcount] = pandas.read_csv(datalocation + "/" + locationofinterest + "_Deaths.csv")
        if parishcounty == "":
            locationlabel = state
        else:
            locationlabel = f'{parishcounty}, {state}'
        if dontdownload == 0:
            locationlist.append(locationlabel)
            if aspercentage.lower() == "yes" or aspercentage.lower() == "y":
                percentageOfPopulation(datalocation, parishcounty, state, locationsdeathdata, locationcount)
            locationcount = locationcount + 1
        anotherlocation = input("Collect data for another location (y/n)? [Enter = n]: ") 
        if anotherlocation == "":
            anotherlocation = "n"
    plotDeathData(datalocation, locationsdeathdata, locationcount, locationlist, aspercentage)

#-----------------------------------------------------#

def plotDeathData(datalocation, locationsdeathdata, locationcount, locationlist, aspercentage):
    x = []
    y = []
    totalrows = len(locationsdeathdata[0].index)
    log = "n"
    log = input("Log Plot (y/n)? [Enter = n]: ")
    plottype = input("Plot Type [Line]: ")
    if plottype == "":
        plottype = "line"
    if log.lower() == "y" or log.lower() == "yes":
        plt.yscale('log')
    locationpointer = 0
    plt.xticks(np.arange(0, totalrows, step=7), rotation=90)
    plt.grid(True)
    while(locationpointer < locationcount):
#        print(locationpointer)
        print(locationlist[locationpointer])
        print(locationsdeathdata[locationpointer])
        plt.plot(locationsdeathdata[locationpointer].Date, locationsdeathdata[locationpointer].Deaths)
        locationpointer = locationpointer + 1
    if aspercentage.lower() == "yes" or aspercentage.lower() == "y":
        plt.ylabel("Deaths as Percentage of Population")
    else:
        plt.ylabel("Deaths")
    plt.xlabel("Date")
    plt.legend(locationlist)
    plt.show()

#-----------------------------------------------------#

def percentageOfPopulation(datalocation, parishcounty, state, locationsdeathdata, locationcount):
    try:
        popdata = pandas.read_csv(datalocation + "/" + "Population.csv")
        popdata = popdata[popdata["State"] == state]
        if(parishcounty != ""):
            popdata = popdata[popdata["Parish/County"] == parishcounty]
        else:
            popdata = popdata.groupby(["State"], as_index=False)["Population"].sum()
#        print(popdata)
        if(parishcounty == ""):
            population = popdata.iloc[0,1].astype(int)
        else:
            population = popdata.iloc[0,2].astype(int)
#        print(population)
        locationsdeathdata[locationcount]["Deaths"] = locationsdeathdata[locationcount]["Deaths"].apply(pandas.to_numeric)
#        print(locationsdeathdata[locationcount])
        locationsdeathdata[locationcount]["Deaths"] = locationsdeathdata[locationcount]["Deaths"].multiply(100)
        locationsdeathdata[locationcount]["Deaths"] = locationsdeathdata[locationcount]["Deaths"].divide(population)
    except Exception as e:
        print(f"Error dividing by population: {e}")
#-----------------------------------------------------#

def additionalPlot(datalocation):
    try:
        log = "n"
        plotanother = input("Additional Plot (y/n)? [Enter = n]: ")
        if plotanother.lower() == "y" or plotanother.lower() == "yes":
            gatherDeathData(datalocation)
        else:
            print("Goodbye!")
    except Exception as e:
        print(f"Error plotting data: {e}")
#-----------------------------------------------------#

def collectDeathData(parishcounty, state, datalocation):
    timenow = datetime.now()    
    timenow_iso = timenow.strftime('%Y-%m-%dT%H:%M:%S')
    deaths_url = 'https://raw.githubusercontent.com/datasets/covid-19/main/data/us_deaths.csv'
    parishcol = "Admin2"
    statecol = "Province/State"
    datecol = "Date"
    deathcol = "Case"
#    state = state.lower()
#    parishcounty = parishcounty.lower()
    createDataFolder(datalocation)
    try:
        if parishcounty == "":
            dailydeathoutput = f'{datalocation}/{state}_Deaths_{timenow_iso}.csv'
            workingdeathoutput = f'{datalocation}/{state}_Deaths.csv'
        else:
            dailydeathoutput = f'{datalocation}/{parishcounty}_{state}_Deaths_{timenow_iso}.csv'
            workingdeathoutput = f'{datalocation}/{parishcounty}_{state}_Deaths.csv'
        print("Downloading death data and creating .csv file...")
        if parishcounty == "":
            deathdata = pandas.read_csv(deaths_url, usecols=[datecol, deathcol, statecol])
            deathdata = deathdata[deathdata[statecol] == state]
            deathdata = deathdata.groupby([datecol], as_index=False)[deathcol].sum()
        else:
            deathdata = pandas.read_csv(deaths_url, usecols=[parishcol, datecol, deathcol, statecol])
            deathdata = deathdata[deathdata[statecol] == state]
            deathdata = deathdata[deathdata[parishcol] == parishcounty]
            deathdata = deathdata.drop(statecol, axis=1)
            deathdata = deathdata.drop(parishcol, axis=1)
        deathdata.columns = ['Date', 'Deaths'] 
        deathdata.to_csv(dailydeathoutput, index=False)
        copyfile(dailydeathoutput, workingdeathoutput)
        if parishcounty == "":
            print(f"File {state}_Deaths_{timenow_iso}.csv saved in {datalocation}")
        else:
            print(f"File {parishcounty}_{state}_Deaths_{timenow_iso}.csv saved in {datalocation}")
    except Exception as e:
        print("Downloading file error: " + str(e))

#-----------------------------------------------------#

def createDataFolder(datalocation):                                                                 
    try:
        if not os.path.exists(datalocation):                                           
            print(f"Directory {datalocation} does not currently exist.")
            print(f"Creating directory {datalocation}")
            os.makedirs(datalocation)                                                  
            print(f"Directory {datalocation} exists. Files will be created there.")
    except Exception as e:
        print("Creating file error: " + str(e))

#-----------------------------------------------------#

main(datalocation)
