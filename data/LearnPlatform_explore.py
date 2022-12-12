#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LearnPlatform data cleaning and exploration

"""

#---------------------------------------------------
# Libraries
#---------------------------------------------------
import  pandas as pd
import glob
import os
import re
import matplotlib.pyplot as plt


#---------------------------------------------------
# Read in the datasets
#---------------------------------------------------

districts=pd.read_csv('/Users/aphan/Documents/JHU/202208 - ML Theory/Project_data/districts_info.csv')
products=pd.read_csv('/Users/aphan/Documents/JHU/202208 - ML Theory/Project_data/products_info.csv')


# pulling in all data for engagment
path='/Users/aphan/Documents/JHU/202208 - ML Theory/Project_data/engagement_data'  

for dirname, _, filenames in os.walk('/Users/aphan/Documents/JHU/202208 - ML Theory/Project_data/engagement_data'):
    for filename in filenames:
        engagement_files = list(glob.glob(os.path.join(dirname,'*.*')))

engagement = pd.DataFrame()

for file in engagement_files:
    district_id = file[79:83]
    engagement_file = pd.read_csv(file)
    engagement_file['id'] = district_id
    engagement = pd.concat([engagement, engagement_file], axis=0).reset_index(drop=True)
    
    

#---------------------------------------------------
# Explore districts dataset
#---------------------------------------------------


# number of missing values
print(f'Number of rows {districts.shape[0]}\nNumber of columns {districts.shape[1]}\nNumber of missing values {sum(districts.isna().sum())} ')
"""
    Number of rows 233
    Number of columns 7
    Number of missing values 442
"""

# Number of missing values in each coulmns
print(districts.isna().sum())
"""
    district_id                   0
    state                        57
    locale                       57
    pct_black/hispanic           57
    pct_free/reduced             85
    county_connections_ratio     71
    pp_total_raw                115
"""

#---------------------------------------------------
# Explore products dataset
#---------------------------------------------------

# number of missing values
print(f'Number of rows {products.shape[0]}\nNumber of columns {products.shape[1]}\nNumber of missing values {sum(products.isna().sum())} ')
"""
    Number of rows 372
    Number of columns 6
    Number of missing values 41 
"""

# Number of missing values in each coulmns
print(products.isna().sum())
"""
    LP ID                          0
    URL                            0
    Product Name                   0
    Provider/Company Name          1
    Primary Essential Function    20

"""

#---------------------------------------------------
# Explore engagment dataset
#---------------------------------------------------

# Number of missing 
print(engagement.isna().sum())

"""
    time                      0
    lp_id                   541
    pct_access            13447
    engagement_index    5378409
    id                        0
"""

list(engagment)
engagement_all.describe()


# number of unique dates, districts, products
engagement_all[].nunique()

"""
time                   366
lp_id                 8556
pct_access            7776
engagement_index    331021
district_id            172
id                       1
"""

# determine how many districts have the full 366 days of data



eng366_dis=engagement.groupby('district_id').time.nunique()
print(eng366_dis['time'].value_counts()['366'])

"""
133 districts have 366 distinct days of engagement data. 
"""

#---------------------------------------------------
# Clean district dataset
#---------------------------------------------------

"""
pct_black/hispanic = % of black/hispanic
pct_free/reduced = % range of students eligible for free or reduced-price lunch 
county_connections_ratio = ratio of residential fixed high-speed connections over 200 kbps in at least one household
pp_total_raw = per-pupil total expenditure

"""

black_hispanic = {
    '[0, 0.2[': '0%-20%',
    '[0.2, 0.4[': '20%-40%',
    '[0.4, 0.6[': '40%-60%',
    '[0.6, 0.8[': '60%-80%',
    '[0.8, 1[': '80%-100%'}

free_reduced = {
    '[4000, 6000[': '4000-6000',
    '[6000, 8000[': '6000-8000',
    '[8000, 10000[': '8000-10000',
    '[10000, 12000[': '10000-12000',
    '[12000, 14000[': '12000-14000',
    '[14000, 16000[': '14000-16000',
    '[16000, 18000[': '16000-18000',
    '[18000, 20000[': '18000-20000',
    '[20000, 22000[': '20000-22000',
    '[22000, 24000[': '22000-24000',
    '[32000, 34000[': '32000-34000'}

connection = {
    '[0.18, 1[': '18%-100%',
    '[1, 2[': '100%-200%'}

# apply the label created above 
districts['pct_black/hispanic'] = districts['pct_black/hispanic'].map(black_hispanic)
districts['pct_free/reduced'] = districts['pct_free/reduced'].map(free_reduced)
districts['county_connections_ratio'] = districts['county_connections_ratio'].map(connection)
districts['pp_total_raw'] = districts['pp_total_raw'].map(free_reduced)
districts.head()

# delete district with missing state
districts=districts[districts["state"].notna()]
    #end up with 176 districts - deleted 57 rows
    
    
districts['district_id'].dtypes
districts['district_id']=districts['district_id'].astype('int64')


#---------------------------------------------------
# Clean product dataset
#---------------------------------------------------
"""
LLC - Learning & curriculum 
CM - Classroom management 
SDO - School & district operation 

"""
# split the essential function column into two columns: Category and sub-category
products[['Category','Sub-Category']]=products['Primary Essential Function'].str.split('-',n=1,expand=True)


# create indicator variables for each of the sectors: corporate, higher ed, preK-12
temp_sectors = products['Sector(s)'].str.get_dummies(sep="; ")
temp_sectors.columns = [f"sector_{re.sub(' ', '', c)}" for c in temp_sectors.columns]
products = products.join(temp_sectors)
products.drop("Sector(s)", axis=1, inplace=True)

del temp_sectors

products['LP ID'].dtypes
#products['LP ID']=products['LP ID'].astype('float64')

#---------------------------------------------------
# Clean engagement dataset
#---------------------------------------------------

# Delete previously created engagement dataframe and create a new one
del engagement

PATH='/Users/aphan/Documents/JHU/202208 - ML Theory/Project_data/engagement_data'  


temp = []

# only keep districts with 366 days of engagement data
for district in districts.district_id.unique():
    df = pd.read_csv(f'{PATH}/{district}.csv', index_col=None, header=0)
    df["district_id"] = district
    if df.time.nunique() == 366:
        temp.append(df)

engagement = pd.concat(temp)
engagement = engagement.reset_index(drop=True)

# Only consider districts and products with full 2020 engagement data
districts_info = districts[districts.district_id.isin(engagement.district_id.unique())].reset_index(drop=True)
products_info = products[products['LP ID'].isin(engagement.lp_id.unique())].reset_index(drop=True)





#---------------------------------------------------
# Merge the datasets together
#---------------------------------------------------

data=engagement.copy()
data['id']=data['id'].astype('int64')
data=data.merge(products,left_on='lp_id',right_on='LP ID',how='left')
data=data.merge(districts,left_on='id',right_on='district_id',how='left')
data['time']=pd.to_datetime(data['time'])

del engagement
del products
del districts

data = data.drop('district_id', axis=1)
data = data.drop('LP ID', axis=1)
data=data.drop('Primary Essential Function',axis=1)
data.head()
