# File can be easily edited to add a different data source urls with different column names, and/or with different locations. 
# This one specifically collects Orleans Parish, Louisiana cases and death data only. 
# - Creates a subfolder called /Data in the file's directory where all the files are saved.
# - Downloads current Covid-19 data into DataFrame and keeps only dates, cases, and deaths for Orleans Parish.
# - Saves timestamped .csv file with dates and cases for Orleans Parish.
# - Overwrites / writes new working .csv file with dates and cases for Orleans Parish.
# - Saves timestamped .csv file with dates and deaths for Orleans Parish.
# - Overwrites / writes new working .csv file with dates and deaths for Orleans Parish.

import urllib.request
import os
import csv
import pandas
from datetime import datetime
from shutil import copyfile

											# Global variables for working file names:
filename = os.path.realpath(__file__)				 			# Current file name
dirname = os.path.dirname(os.path.realpath(__file__)) 					# Directory of this file
datalocation = dirname + "/Data" 							# Location where data will be saved

timenow = datetime.now() 								# Collect current time
timenow_iso = timenow.strftime('%Y-%m-%dT%H:%M:%S') 					# Convert current time to string

cases_url = 'https://github.com/datasets/covid-19/raw/master/data/us_confirmed.csv'	# URL of location of data for US cases
deaths_url = 'https://github.com/datasets/covid-19/raw/master/data/us_deaths.csv'	# URL of location of data for US deaths

locationcol = "Combined_Key"								# Column of data for location of interest
casecol = "Case" 									# Column where cases are located
datecol = "Date" 									# Column where dates are located
deathcol = "Case" 									# Column where deaths are located

locationofinterest = "Orleans, Louisiana, US"

#-----------------------------------------------------#

def createDataFolder(): 								# Data collection function
    print("Starting File: ", filename)
    try:
        if not os.path.exists(datalocation): 						# Check for Data file in current directory
            print(f"Directory {datalocation} does not currently exist.")
            print(f"Creating directory {datalocation}")
            os.makedirs(datalocation) 							# Create data file in current directory if none exists
        else:
            print(f"Directory {datalocation} exists. File will be created there.")
    except Exception as e:
        print("Creating file error: " + str(e))

#-----------------------------------------------------#

def collectOrleansCaseData():
    try:
        dailycaseoutput = f'{datalocation}/OrleansParishCases_{timenow_iso}.csv'	# Current data file name
        workingcaseoutput = f'{datalocation}/OrleansParishCases.csv' 			# Working data file name
        print("Downloading case data and creating .csv file...")
        casedata = pandas.read_csv(cases_url, usecols=[locationcol,datecol,casecol]) 	# Load case data into dataframe
        casedata = casedata[casedata[locationcol] == locationofinterest] 		# Filter data to include only location of interest
        casedata = casedata.drop(locationcol, axis=1) 					# Delete location of interest column
        casedata.to_csv(dailycaseoutput, index=False) 					# Save to current case output file
        copyfile(dailycaseoutput, workingcaseoutput) 					# Copy current case to working file
        print(f"File OrleansParishCases.csv saved in {datalocation}")
    except Exception as e:
        print("Downloading file error: " + str(e))

#-----------------------------------------------------#

def collectOrleansDeathData():
    try:
        dailydeathoutput = f'{datalocation}/OrleansParishDeaths_{timenow_iso}.csv'
        workingdeathoutput = f'{datalocation}/OrleansParishDeaths.csv'
        print("Downloading death data and creating .csv file...")
        deathdata = pandas.read_csv(deaths_url, usecols=[locationcol,datecol,deathcol])
        deathdata = deathdata[deathdata[locationcol] == locationofinterest]
        deathdata = deathdata.drop(locationcol, axis=1)
        deathdata.to_csv(dailydeathoutput, index=False)
        copyfile(dailydeathoutput, workingdeathoutput)
        print(f"File OrleansParishDeaths.csv saved in {datalocation}")
    except Exception as e:
        print("Downloading file error: " + str(e))


#-----------------------------------------------------#

createDataFolder()

collectOrleansCaseData()

collectOrleansDeathData()
