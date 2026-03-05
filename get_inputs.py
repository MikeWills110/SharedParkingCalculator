# PROGRAMMER: Joshua Cayanan
# DATE CREATED: May 25, 2020

import os
import argparse
import pandas as pd
import unicodedata

def normalize_text(text):
    """Normalize unicode characters to handle curly apostrophes and other special characters"""
    # Use unicode character codes for curly apostrophes
    text = text.replace('\u2019', "'")  # Right single quotation mark (')
    text = text.replace('\u2018', "'")  # Left single quotation mark (')
    text = text.replace('\u00b4', "'")  # Acute accent
    text = text.replace('\u0060', "'")  # Grave accent
    return text

def normalize_dataframe_index(df):
    """Normalize all index values in a dataframe and remove NaN indices"""
    # Remove rows with NaN index
    df = df[df.index.notna()]
    # Normalize index values
    df.index = df.index.map(normalize_text)
    # Remove duplicate index values (keep first occurrence)
    df = df[~df.index.duplicated(keep='first')]
    return df

def get_working_directory():
    '''
    Inputs working directory from user to direct terminal to location of inputs, scripts, and where to save outputs

    Parameters:
      None - simply uses argparse module to craete and store command line arguments

    Returns:
      parse_args() - data structure that stores the command line arguments object
    '''

    #Create parser object
    parser = argparse.ArgumentParser()

    #Create 1 command line argument for working directory
    parser.add_argument('--dir', type = str, help = 'path to shared parking program in your project folder')

    #Return the given working directory
    return parser.parse_args()

def get_inputs():
    #Get working directory from command line input
    in_arg = get_working_directory()
    input_directory = os.path.join(in_arg.dir, "Inputs")
    os.chdir(input_directory)

    #Import base parking demand from a CSV into a Pandas dataframe
    base_parking_demand = pd.read_csv('BaseParkingDemand.csv', index_col = 0)
    base_parking_demand = normalize_dataframe_index(base_parking_demand)

    #Import customer vs employee split CSV into a Pandas dataframe
    customer_employee_split = pd.read_csv('CustomerEmployeeSplit.csv', index_col = 0)
    customer_employee_split = normalize_dataframe_index(customer_employee_split)

    #Import customer/staff and time-of-day data from a CSV into a Pandas dataframe
    tod_weekday = pd.read_csv('TimeOfDayWeekday.csv', index_col = 0)
    tod_weekday = normalize_dataframe_index(tod_weekday)

    tod_weekend = pd.read_csv('TimeOfDayWeekend.csv', index_col = 0)
    tod_weekend = normalize_dataframe_index(tod_weekend)

    #Import noncpative adjustment data from a CSV into a Pandas dataframe
    noncaptive_weekday = pd.read_csv('NoncaptiveAdjustmentWeekday.csv', index_col = 0)
    noncaptive_weekday = normalize_dataframe_index(noncaptive_weekday)

    noncaptive_weekend = pd.read_csv('NoncaptiveAdjustmentWeekend.csv', index_col = 0)
    noncaptive_weekend = normalize_dataframe_index(noncaptive_weekend)

    #Import monthly adjustment data from a CSV into a Pandas dataframe
    monthly_factors = pd.read_csv('MonthlyAdjustment.csv', index_col = 0)
    monthly_factors = normalize_dataframe_index(monthly_factors)

    return base_parking_demand, customer_employee_split, tod_weekday, tod_weekend, \
           noncaptive_weekday, noncaptive_weekend, monthly_factors