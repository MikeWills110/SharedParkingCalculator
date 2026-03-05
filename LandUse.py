# PROGRAMMER: Joshua Cayanan
# DATE CREATED: May 25, 2020

import numpy as np
import pandas as pd
import os
from get_inputs import get_inputs

# Save the original working directory before get_inputs changes it
original_dir = os.getcwd()

#Call the get_inputs function
base_parking_demand, customer_employee_split, tod_weekday, tod_weekend, \
noncaptive_weekday, noncaptive_weekend, monthly_factors = get_inputs()

# Return to the original working directory
os.chdir(original_dir)

#Create a Class for ULI land use categories
class LandUse():
    def __init__(self, name):
        self.name = name

    def compute_parking(self, context, base_parking_demand, customer_employee_split, tod, noncaptive, monthly):
        #Concatenate user type suffixes to land use name for subsequent dataframe match row to string search
        customer_row_namer = self.name + 'Customer'
        employee_row_namer = self.name + 'Employee'

        #Extract appropriate rows based on land use name from common dataframes
        df_1 = base_parking_demand
        daily_demand = df_1.loc[self.name, context]

        df_2 = customer_employee_split
        customer_split = df_2.loc[self.name, 'Customer' + context]
        employee_split = df_2.loc[self.name, 'Employee' + context]

        df_3 = tod
        customer_tod = df_3.loc[customer_row_namer, :]
        employee_tod = df_3.loc[employee_row_namer, :]

        df_4 = noncaptive
        customer_noncaptive = df_4.loc[customer_row_namer, :]
        employee_noncaptive = df_4.loc[employee_row_namer, :]

        df_5 = monthly
        # Extract individual monthly factors for this land use's customer and employee components
        customer_monthly = df_5.loc[customer_row_namer, :]
        employee_monthly = df_5.loc[employee_row_namer, :]

        #Calculate the parking demand, adjusted for customer/staff split, time of day profiles, noncaptive, and monthly effects
        parking_demand_yearly = []
        for month in months:
            parking_demand_customer = daily_demand * customer_split * customer_tod * customer_noncaptive * customer_monthly[month]
            parking_demand_employee = daily_demand * employee_split * employee_tod * employee_noncaptive * employee_monthly[month]
            total_demand = parking_demand_customer + parking_demand_employee

            # Replace any NaN values with 0 before converting to int
            total_demand = total_demand.fillna(0)
            # Convert to list, rounding each value
            parking_demand_total = [int(np.rint(x)) for x in total_demand.values]
            parking_demand_total.append(month)

            parking_demand_yearly.append(parking_demand_total)

        return parking_demand_yearly

    def reshape_data(data_dictionary):

        data_list = []
        for i in range(0, 12):
            for key, value in data_dictionary.items():
                row = [key] + value[i]
                data_list.append(row)

        #Convert to pandas df and apply transformations to reshape the data
        df = pd.DataFrame(data_list, columns = col_names)
        df = df.melt(['Land Use', 'Month'], value_vars = times, var_name = 'Time', value_name = 'Parking')
        df['Month'] = pd.Categorical(df['Month'], categories = months, ordered = True)
        df['Time'] = pd.Categorical(df['Time'], categories = times, ordered = True)
        df.sort_values(by = ['Month', 'Time'], inplace = True)
        df.reset_index(drop = True, inplace = True)

        df = df.pivot_table(values = 'Parking', index = ['Month', 'Time'], columns = ['Land Use'], \
                            fill_value = 0, aggfunc = 'first')

        #Create a new total column
        df['Total'] =df.sum(axis = 1)

        return df

#Dataframe columns in list format - using 24-hour format (0-23)
times = [str(i) for i in range(24)]
col_names = ['Land Use'] + times + ['Month']
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

#Initialise land use objects
areas = base_parking_demand.index
land_uses = {name: LandUse(name) for name in areas}

#Create function for weekday and weekend parking demand
def parking_demand(context):
    if context == 'Weekday':
        tod, noncaptive = tod_weekday, noncaptive_weekday
    else:
        tod, noncaptive = tod_weekend, noncaptive_weekend
    parking_demand_dict = {}
    for land_use in land_uses.values():
        parking_demand_dict[land_use.name] = land_use.compute_parking(context, base_parking_demand, customer_employee_split, \
                                        tod, noncaptive, monthly_factors)
    return LandUse.reshape_data(parking_demand_dict)

# Main execution - compute parking demand for weekday and weekend
if __name__ == '__main__':
    
    # Create Outputs directory if it doesn't exist
    output_dir = os.path.join(original_dir, 'Outputs')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Compute parking demand for weekday and weekend
    print("Computing weekday parking demand...")
    weekday_df = parking_demand('Weekday')
    
    print("Computing weekend parking demand...")
    weekend_df = parking_demand('Weekend')
    
    # Save to CSV files
    weekday_path = os.path.join(output_dir, 'ParkingDemand_Weekday.csv')
    weekend_path = os.path.join(output_dir, 'ParkingDemand_Weekend.csv')
    
    weekday_df.to_csv(weekday_path)
    weekend_df.to_csv(weekend_path)
    
    print(f"Weekday parking demand saved to {weekday_path}")
    print(f"Weekend parking demand saved to {weekend_path}")
    print("Done!")