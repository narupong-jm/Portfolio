import requests
import time
import pandas as pd

url = "http://universities.hipolabs.com/search?country=United+States"
nums = []
unis_name = []
num = 1

for i in range(10):
    resp = requests.get(url)
    nums.append(num)
    if resp.status_code == 200:
        uni_name = resp.json()[i]["name"]
        unis_name.append(uni_name)
    else:
        unis_name.append("error")
    time.sleep(1)
    num += 1

df = pd.DataFrame( data = {
    "university_name": unis_name
}, index= nums)

df.head(5)
