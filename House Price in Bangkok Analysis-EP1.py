from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import re
import requests
import pandas as pd

url_main = "https://www.thailand-property.com/houses-for-sale/bangkok"
url_total = 10

title_list = []
location_list = []
price_list = []
beds_list = []
baths_list = []
usable_area_list = []
land_area_list = []
floors_list = []
facilities_list = []

for page in range(1, url_total+1):
    if page == 1:
        url_page = url_main
    else:
        url_page = f"{url_main}?page={page}"

    req_page = Request(url_page, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req_page).read()

    soup = BeautifulSoup(webpage, 'html.parser')

    listing_links = soup.select('div.left-block a.hj-listing-snippet')
    urls = [link['href'] for link in listing_links]
    
    for url_seller in urls:
        req_seller = Request(url_seller, headers={'User-Agent': 'Mozilla/5.0'})
        web_seller = urlopen(req_seller).read()
        soup_seller = BeautifulSoup(web_seller, 'html.parser')

        title = soup_seller.select_one('h1.page-title')
        location = soup_seller.select_one('div.location')
        price = soup_seller.select_one('div.price-title')
        beds = soup_seller.select_one('li:contains("Beds") span')
        baths = soup_seller.select_one('li:contains("Baths") span')
        usable_area = soup_seller.select_one('li:contains("Usable area") span')
        land_area = soup_seller.select_one('li:contains("Land area") span')
        floors = soup_seller.select_one('li:contains("Floors") span')
        facilities_elements = soup_seller.select('.list-unstyled.facilities li')
        facilities = [facility.get_text(strip=True) for facility in facilities_elements]

        title_list.append(title.text.strip() if title else None)
        location_list.append(location.text.strip() if location else None)
        price_list.append(re.search(r'Sale: ฿ ([\d,]+)', price.text).group(1) if price else None)
        beds_list.append(beds.text if beds else None)
        baths_list.append(baths.text if baths else None)
        usable_area_list.append(float(re.search(r'\d+(\.\d+)?', usable_area.text).group()) if usable_area else None)
        land_area_list.append(float(re.search(r'\d+(\.\d+)?', land_area.text).group()) if land_area else None)
        floors_list.append(floors.text if floors else None)
        facilities_list.append(facilities)

house_detail = {
    'title': title_list,
    'location': location_list,
    'beds': beds_list,
    'baths': baths_list,
    'usable_area': usable_area_list,
    'land_area': land_area_list,
    'floors': floors_list,
    'facilities': facilities_list,
    'price': price_list,
}

housePrice_df = pd.DataFrame(house_detail, dtype=object)
facilities_df = pd.get_dummies(housePrice_df['facilities'].explode()).groupby(level=0).sum()
housePrice_df = pd.concat([housePrice_df, facilities_df], axis=1)
housePrice_df = housePrice_df.drop('facilities', axis=1)
housePrice_df
