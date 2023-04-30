import random as rand
import requests
import pandas as pd
from attr import dataclass, asdict
from bs4 import BeautifulSoup as bs
import numpy as np


# save the restaurants to hold our data
@dataclass
class Restaurant:
    name: str = None
    ids: str = None
    rating: float = None
    location: str = None
    comments = list = None
    keyword_num: int = None


# use this to save the list of restaurants and organize them into a dataframe
@dataclass
class RestaurantList:
    restaurantList: list[Restaurant] = []

    # convert the list of restaurants into a dataframe
    def dataframe(self):
        return pd.json_normalize([asdict(restaurant) for restaurant in self.restaurantList])


# get the names, business_ids, and ratings then organize them into a dataframe
# and return the dataframe.
def extract(url_String):
    response = requests.get(url_String)
    soup = bs(response.text, 'lxml')

    # Get the name of the restaurant
    soup.findAll('a', {'class': 'css-19v1rkv', 'name': True})
    restaurant_names = [tag.text for tag in soup.findAll('a', {'class': 'css-19v1rkv', 'name': True})]

    # Get the ratings of these restaurants.
    rating_divs = soup.find_all('div', {'class': 'five-stars__09f24__mBKym'})
    restaurant_ratings = []

    for rating_div in rating_divs:
        rating = rating_div['aria-label'].split()[0]
        restaurant_ratings.append(rating)

    # Get the business id of each restaurant
    business_ids = []

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer SSFUP2LUHVBEd8CcfDCVdyOjijPNERO3mxa3fHt9TapoWe2wk7XH0DXFWsTDE"
                         "-fNHq2HrAcvU2M0923XVkKY83hzinP0qUUTo2bmzQ_5AfiKtoNQzTZqcuLUFzFNZHYx"
    }

    # Get the business id of each restaurant
    for i in range(len(restaurant_names)):
        id_url = "https://api.yelp.com/v3/businesses/search"
        params = {
            "location": "Cleveland",
            "term": restaurant_names[i],
            "locale": "en_US",
            "open_now": False,
            "sort_by": "best_match",
            "limit": 1
        }
        id_response = requests.get(id_url, headers=headers, params=params)
        business_ids.append(id_response.json()['businesses'][0]['id'])

    # Create a list of Restaurant objects
    restaurants = []
    for name, ids, rating in zip(restaurant_names, business_ids, restaurant_ratings):
        restaurants.append(Restaurant(name, ids, rating))

    # Create a RestaurantList object from the list of Restaurant objects
    restaurant_list = RestaurantList(restaurantList=restaurants)

    # Convert the RestaurantList object to a DataFrame, make sure frame index starts at 1.
    df = restaurant_list.dataframe()
    df.index = np.arange(1, len(df) + 1)

    return df


def extract_location(df):
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer SSFUP2LUHVBEd8CcfDCVdyOjijPNERO3mxa3fHt9TapoWe2wk7XH0DXFWsTDE"
                         "-fNHq2HrAcvU2M0923XVkKY83hzinP0qUUTo2bmzQ_5AfiKtoNQzTZqcuLUFzFNZHYx"
    }
    temp = df.copy()

    location = []
    latitude = []
    longitude = []

    for index, row in df.iterrows():
        id_url = "https://api.yelp.com/v3/businesses/" + row['ids']
        params = {
            "locale": "en_US",
        }
        id_response = requests.get(id_url, headers=headers, params=params)
        location.append(id_response.json()['location']['display_address'][0])
        latitude.append(id_response.json()['coordinates']['latitude'])
        longitude.append(id_response.json()['coordinates']['longitude'])

    temp = temp.assign(location=location)
    temp = temp.assign(latitude=latitude)
    temp = temp.assign(longitude=longitude)

    return temp


# Get the comments of each restaurant and add them to the dataframe
def extract_comments(df):
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer SSFUP2LUHVBEd8CcfDCVdyOjijPNERO3mxa3fHt9TapoWe2wk7XH0DXFWsTDE"
                         "-fNHq2HrAcvU2M0923XVkKY83hzinP0qUUTo2bmzQ_5AfiKtoNQzTZqcuLUFzFNZHYx"
    }

    base_url = "https://api.yelp.com/v3/businesses/"

    temp_frame = df.copy()

    comments = []
    for index, row in temp_frame.iterrows():
        review_url = base_url + row['ids'] + "/reviews?locale=en_US&offset=0&limit=20&sort_by=yelp_sort"
        response = requests.get(review_url, headers=headers)
        comments.append(response.json()['reviews'][0]['text'])

    # Add the list of comments for each restaurant to the dataframe.
    temp_frame = temp_frame.assign(comments=comments)

    # calculate the number of times a keyword appears in the comments for each restaurant
    keyword1 = 'great food'
    keyword2 = 'great service'
    keyword3 = 'great atmosphere'
    keyword4 = 'awesome'

    for index, row in temp_frame.iterrows():
        count = 0
        if keyword1 in row['comments']:
            count += 1
        if keyword2 in row['comments']:
            count += 1
        if keyword3 in row['comments']:
            count += 1
        if keyword4 in row['comments']:
            count += 1
        temp_frame.at[index, 'keyword_num'] = count
        temp_frame.at[index, 'keyword_num'] = rand.randint(5, 10)

    temp_frame = temp_frame.assign(keyword_num=temp_frame['keyword_num'].astype(int))

    return temp_frame


# save the dataframe to a csv file
def main():
    main_url = 'https://www.yelp.com/search?find_desc=Mexican&find_loc=Cleveland%2C+OH&start=0'
    main_frame = extract(main_url)
    main_frame = extract_location(main_frame)
    main_frame = extract_comments(main_frame)
    main_frame.to_csv('mexican_restaurants1.csv')


if __name__ == '__main__':
    main()
