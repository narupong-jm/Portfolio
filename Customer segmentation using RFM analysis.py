## imports the sqlite3 module in the program
# sqlite3 serve interface for interacting with SQLite databases.
import sqlite3
import pandas as pd

try:
    ## Use the connect() method of the connector class with the database name. To establish a connection to SQLite.
    conn = sqlite3.connect('retail_data.db')

    ## Use the cursor() method of a connection class to create a cursor object to execute or interact with the database SQLite command/queries from Python. 
    cursor = conn.cursor()
    print("Successfully Connected to SQLite")
    
    ## Load the data into a DataFrame
    ## Focuesd the order in UK and filter cancel order out
    sales_uk = pd.read_sql_query("SELECT * FROM retail WHERE Country = 'United Kingdom' AND Quantity > 0", conn)
    print("Retail in UK", sales_uk)

    ## Write the sales_UK dataframe to CSV file
    sales_uk.to_csv("Retail_in_UK.csv")

    ## Use cursor.clsoe() method to close the cursor
    cursor.close()

except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)
finally:
    ## Use connection.clsoe() method to close the SQLite connections.
    if conn:
        conn.close()
        print("The SQLite connection is closed")


####################################################################################################################################################################

import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns 

## 1) Get the data
# Define the data types of columns while reading a CSV file.
dtype_mapping = {
    'InvoiceNo' : 'string',
    'StockNo' : 'string',
    'CustomerID' : 'string'
}
# Create Data frame called 'sales_in_uk' by CSV file reading.
sales_in_uk = pd.read_csv('Retail_in_UK.csv', encoding="ISO-8859-1", dtype=dtype_mapping)
# Set the first column as index
sales_in_uk.set_index(sales_in_uk.columns[0], inplace=True)
# Print Top 10 of sales_in_uk
sales_in_uk.head(10)

## Data preparation
# Check number of row and column
sales_in_uk.shape

# Remove rows that CustomerID are null value.
sales_in_uk.dropna(subset=['CustomerID'], how='all', inplace=True)
# Check number of row and column again
sales_in_uk.shape

# Check data type of InvoiceDate
sales_in_uk['InvoiceDate'].dtype

# 'dtype('O') indicates that the data type of a column is 'object'.
# Convert the InvoiceDate that is an objects to the datetime format and store them in a new column
sales_in_uk['InvoiceDate'] = pd.to_datetime(sales_in_uk['InvoiceDate'])
# Check data type of InvoiceDate again
sales_in_uk['InvoiceDate'].dtype

# dtype('<M8[ns]') indicates that the data type of a column is datetime64[ns].
# Focused on YEAR 2023
sales_2023 = sales_in_uk[sales_in_uk['InvoiceDate']> "2022-12-31"]
sales_2023.shape

# Summary data that is prepared completely.
print("Summary of Data preparation")
print("Number of Transaction : ",sales_2023['InvoiceNo'].nunique())
print("Number of Product that is bought : ",sales_2023['StockCode'].nunique())
print("Number of Customer : ",sales_2023['CustomerID'].nunique())
print("Total of Sales Quantity : ",sales_2023['Quantity'].sum())
print("Total of Revenue in 2023 : ",round((sales_2023['Quantity']*sales_2023['UnitPrice']).sum(),0))
print("Percentage of CustomersID that are null value : ",round(sales_2023['CustomerID'].isnull().sum()*100 / len(sales_2023),2)," %")

'''
RFM Analysis
- Recency (R): Recency refers to how recently a customer has made a purchase.
- Frequency (F): Frequency represents how often a customer makes purchases within a specific period, such as a month or a year.
- Monetary Value (M): Monetary value refers to the total amount of money a customer has spent on purchases.
'''

## Recency Calculate
# To calculate recency, we need to choose a date point from which we evaluate how many days ago was the customer's last purchase.
# last date available in our dataset
last_date = sales_2023['InvoiceDate'].max()
print("Last date purchasing : ", last_date)

# We will use the last date : 2023-12-09 is reference.
now = dt.date(2023,12,9)
print(now)

# Create a new column called 'date' which contain the date of invoice.
sales_2023['date'] = pd.DatetimeIndex(sales_2023['InvoiceDate']).date
sales_2023.head(10)

# Group by CustomerID and Get last date of purchase
r_df = sales_2023.groupby(by='CustomerID', as_index=False)['date'].max()
r_df.columns = ['CustomerID','LastPurchaseDate']
r_df.head(10)

# Calculate Recency
r_df['Recency'] = r_df['LastPurchaseDate'].apply(lambda x : (now - x).days)
r_df.head(10)

# Remove column 'LastPurchaseDate' which we don't use it anymore.
r_df.drop('LastPurchaseDate',axis=1, inplace=True)
r_df.head(10)

## Frequency Calculate
# To find frequency, we need to check how many invoices are registered by the same customer.
# Remove duplicates value.
sales_2023_copy = sales_2023
print(sales_2023_copy.shape)
sales_2023_copy.drop_duplicates(subset=['InvoiceDate','CustomerID'],keep='first',inplace=True)
print(sales_2023_copy.shape)

# Calculate Frequency
f_df = sales_2023_copy.groupby(by=['CustomerID'], as_index=False)['InvoiceNo'].count()
f_df.columns = ['CustomerID','Frequency']
f_df.head(10)

## Monetary
# To find Monetary, we will create a new column total cost to have the total price per invoice.
# Create column total cost
sales_2023['TotalCost'] = sales_2023['Quantity'] * sales_2023['UnitPrice']

# Calculate Monetary
m_df = sales_2023.groupby(by='CustomerID', as_index=False).agg({'TotalCost': 'sum'})
m_df.columns = ['CustomerID', 'Monetary']
m_df.head(10)

## Create RFM table
# Merge Recency dataframe with Frequency dataframe
rf_df = r_df.merge(f_df,on='CustomerID')
rf_df.head(10)

# Merge rf dataframe with m dataframe
rfm_df = rf_df.merge(m_df,on='CustomerID')
rfm_df.head(10)

# Set CustomerID as the index
rfm_df.set_index('CustomerID',inplace=True)
rfm_df.head(10)

## RFM table Correctness Verification
Cus_Insp_df = sales_2023[sales_2023['CustomerID']=='12820']
Cus_Insp_df

print('Last purchase of 12820',Cus_Insp_df['date'].max())
print('Recency of 12820: ', rfm_df.loc['12820','Recency'])

(now - dt.date(2023,12,6)).days == 3

'''
## Customer segments with RFM Model

The simplest way to create customers segments from RFM Model is to use Quartiles. We assign a score from 1 to 4 to Recency, Frequency and Monetary. 
Four is the best/highest value, and one is the lowest/worst value. A final RFM score is calculated simply by combining individual RFM score numbers.

Note: Quintiles (score from 1-5) offer better granularity, in case the business needs that but it will be more challenging to 
create segments since we will have 555 possible combinations. So, we will use quartiles.
'''

## RFM Quartiles
rfm_qua = rfm_df.quantile(q=[0.25,0.5,0.75])
rfm_qua

# Transform to Dict data type
rfm_qua.to_dict()

## Creation of RFM Segmentation
# We will create two segmentation classes since, high recency is bad, while high frequency and monetary value is good.

# First segmentation : Recency
# Arguments (x = value, p = recency, monetary_value, frequency, d = quartiles dict)
def RScore(x,p,d):
    if x <= d[p][0.25]:
        return 4
    elif x <= d[p][0.50]:
        return 3
    elif x <= d[p][0.75]: 
        return 2
    else:
        return 1

# Second segmentation : Frequency & Monetary
# Arguments (x = value, p = recency, monetary_value, frequency, k = quartiles dict)
def FMScore(x,p,d):
    if x <= d[p][0.25]:
        return 1
    elif x <= d[p][0.50]:
        return 2
    elif x <= d[p][0.75]: 
        return 3
    else:
        return 4

#create rfm segmentation table
rfm_segmentation = rfm_df
rfm_segmentation['R'] = rfm_segmentation['Recency'].apply(RScore, args=('Recency',rfm_qua))
rfm_segmentation['F'] = rfm_segmentation['Frequency'].apply(FMScore, args=('Frequency',rfm_qua))
rfm_segmentation['M'] = rfm_segmentation['Monetary'].apply(FMScore, args=('Monetary',rfm_qua))
rfm_segmentation.head(10)

'''
Now that we have the score of each customer, 
we can represent our customer segmentation. 
First, we need to combine the scores (R, F, M) together.
'''
rfm_segmentation['RFM_Score'] = rfm_segmentation.R.map(str) \
                            + rfm_segmentation.F.map(str) \
                            + rfm_segmentation.M.map(str)
rfm_segmentation.head(10)

'''
- Best Recency score = 4: most recently purchase. 
- Best Frequency score = 4: most quantity purchase. 
- Best Monetary score = 4: spent the most.
Let's see who are our Champions (best customers).
'''
rfm_segmentation[rfm_segmentation['RFM_Score']=='444'].sort_values('Monetary', ascending=False).head(10)

'''
We can find here a suggestion of key segments and then we can decide which segment to consider for further study.
Note: the suggested link use the opposite valuation: 1 as highest/best score and 4 is the lowest.
How many customers do we have in each segment?
'''
print("Best Customers: ",len(rfm_segmentation[rfm_segmentation['RFM_Score']=='444']))
print('Loyal Customers: ',len(rfm_segmentation[rfm_segmentation['F']==4]))
print("Big Spenders: ",len(rfm_segmentation[rfm_segmentation['M']==4]))
print('Almost Lost: ', len(rfm_segmentation[rfm_segmentation['RFM_Score']=='244']))
print('Lost Customers: ',len(rfm_segmentation[rfm_segmentation['RFM_Score']=='144']))
print('Lost Cheap Customers: ',len(rfm_segmentation[rfm_segmentation['RFM_Score']=='111']))


'''
Segment customers using Python. Group them into ten segments:  
  - Champion : 3.4 < r <= 4, 10 < FxM <= 16.  
  - Loyal : 2.2 < r <= 3.4, 10 < FxM <= 16.  
  - Cannot Lose Them : 1 <= r =< 2.2, 10 < FxM <= 16.  
  - Potential Loyalist : 2.8 < r <= 4, 6 < FxM <= 10.  
  - Need Attention : 2.2 < r <= 2.8, 6 < FxM <= 10.  
  - At Risk : 1 <= r <= 2.2, 6 < FxM <= 10.  
  - New Customer : 3.4 < r <= 4, 1 <= FxM <= 6.  
  - Promising : 2.8 < r <= 3.4, 1 <= FxM <= 6.  
  - About to Sleep : 2.2 < r <= 2.8, 1 <= FxM <= 6.  
  - Hilbernating : 1 <= r <= 2.2, 1 <= FxM <= 6.  
'''

rfm_segment = rfm_segmentation.copy()

# Create function for define cluster code
def assign_clusterCode(row):
    if row['F'] * row['M'] > 10 and row['F'] * row['M'] <= 16 and row['R'] > 3.4 and row['R'] <= 4:
        return 1
    elif row['F'] * row['M'] > 10 and row['F'] * row['M'] <= 16 and row['R'] > 2.2 and row['R'] <= 3.4:
        return 2
    elif row['F'] * row['M'] > 10 and row['F'] * row['M'] <= 16 and row['R'] >= 1 and row['R'] <= 2.2:
        return 3
    elif row['F'] * row['M'] > 6 and row['F'] * row['M'] <= 10 and row['R'] > 2.8 and row['R'] <= 4: 
        return 4
    elif row['F'] * row['M'] > 6 and row['F'] * row['M'] <= 10 and row['R'] > 2.2 and row['R'] <= 2.8:
        return 5
    elif row['F'] * row['M'] > 6 and row['F'] * row['M'] <= 10 and row['R'] >= 1 and row['R'] <= 2.2:
        return 6
    elif row['F'] * row['M'] >= 1 and row['F'] * row['M'] <= 6 and row['R'] > 3.4 and row['R'] <= 4:
        return 7
    elif row['F'] * row['M'] >= 1 and row['F'] * row['M'] <= 6 and row['R'] > 2.8 and row['R'] <= 3.4:
        return 8
    elif row['F'] * row['M'] >= 1 and row['F'] * row['M'] <= 6 and row['R'] > 2.2 and row['R'] <= 2.8:
        return 9
    else:
        return 10

# Apply function to each row to create 'Cluster' column
rfm_segment['ClusterCode'] = rfm_segment.apply(assign_clusterCode, axis=1)
rfm_segment.head(10)

# Create function for define cluster name 10
def assign_clusterName(row):
    if row['F'] * row['M'] > 10 and row['F'] * row['M'] <= 16 and row['R'] > 3.4 and row['R'] <= 4:
        return 'Champion'
    elif row['F'] * row['M'] > 10 and row['F'] * row['M'] <= 16 and row['R'] > 2.2 and row['R'] <= 3.4:
        return 'Loyal'
    elif row['F'] * row['M'] > 10 and row['F'] * row['M'] <= 16 and row['R'] >= 1 and row['R'] <= 2.2:
        return 'Cannot Lose them'
    elif row['F'] * row['M'] > 6 and row['F'] * row['M'] <= 10 and row['R'] > 2.8 and row['R'] <= 4: 
        return 'Potential Loyalist'
    elif row['F'] * row['M'] > 6 and row['F'] * row['M'] <= 10 and row['R'] > 2.2 and row['R'] <= 2.8:
        return 'Need Attention'
    elif row['F'] * row['M'] > 6 and row['F'] * row['M'] <= 10 and row['R'] >= 1 and row['R'] <= 2.2:
        return 'At risk'
    elif row['F'] * row['M'] >= 1 and row['F'] * row['M'] <= 6 and row['R'] > 3.4 and row['R'] <= 4:
        return 'New Customer'
    elif row['F'] * row['M'] >= 1 and row['F'] * row['M'] <= 6 and row['R'] > 2.8 and row['R'] <= 3.4:
        return 'Promising'
    elif row['F'] * row['M'] >= 1 and row['F'] * row['M'] <= 6 and row['R'] > 2.2 and row['R'] <= 2.8:
        return 'About to Sleep'
    else:
        return 'Hibernating'

# Apply function to each row to create 'Cluster' column
rfm_segment['ClusterName'] = rfm_segment.apply(assign_clusterName, axis=1)
rfm_segment.head(10)

# Create column FxM
rfm_segment['FxM'] = rfm_segment['F'] * rfm_segment['M']
rfm_segment.head(10)

# Define customer segments
segments = {
    1: "Champion",
    2: "Loyal",
    3: "Cannot loss them",
    4: "Potential Loyalist",
    5: "Need Attention",
    6: "At risk",
    7: "New Customer",
    8: "Promising",
    9: "About to Sleep",
    10: "Hibernating"
}

# Define colors for each segment
colors = {
    "Champion" : "gold",
    "Loyal" : "silver",
    "Cannot loss them" : "orange",
    "Potential Loyalist" : "green",
    "Need Attention" : "blue",
    "At risk" : "red",
    "New Customer" : "pink",
    "Promising" : "brown",
    "About to Sleep" : "gray",
    "Hibernating" : "black"
}

# Plot scatter plot with legend
plt.figure(figsize=(10, 6))
for segment, group in rfm_segment.groupby('ClusterCode'):
    label = segments[segment]
    color = colors[label]
    plt.scatter(group['R'], group['FxM'], label=label, color=color)
    # Annotate each point with CustomerID
    for customer_id, r, f in zip(group.index, group['R'], group['FxM']):
        plt.annotate(customer_id, (r, f), fontsize=8)


plt.xlabel('Recency')
plt.ylabel('Frequency X Monetary')
plt.title('Customer Segmentation')
plt.legend(loc='right', bbox_to_anchor=(1.4, 0.5), ncol=1)
plt.show()
