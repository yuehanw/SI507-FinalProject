import requests
import json
import sqlite3
import secrets
from requests_oauthlib import OAuth1
from bs4 import BeautifulSoup
from flask import Flask, render_template, url_for

app = Flask(__name__)
DBNAME = "yhFinalProj.db"
CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}

class City:
    def __init__(self, rank = None,cityName = None, stateName = None):
        self.cityName = cityName
        self.rank = rank
        # self.stateName = stateName

    def __repr__(self):
        return "{}. {}".format(self.rank, self.cityName)

def load_cache(): 
    ''' Load to create a cache file."

    Parameters
    ----------
    None 

    Returns
    -------
    file
        a cache file
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_contents = cache_file.read()
        cache = json.loads(cache_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache): 
    ''' Load the cache file"

    Parameters
    ----------
    cache:
        a python file

    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):
    ''' Check the cache to determine whether to use cache or fetch"

    Parameters
    ----------
    url: string
    cache: dict

    Returns
    -------
    dict
        key is a url name and value is the url
    '''
    print(cache.keys())

    if url in cache.keys(): 
        print("Using cache")
        return cache[url]     
    else:
        print("Fetching")
        response = requests.get(url) 
        cache[url] = response.text 
        save_cache(cache)
        return cache[url]     
CACHE_DICT = load_cache()

# Scrape the Page
def get_city_names():
    '''scrape the url page and return a cities dict'''
    cities = {}

    page_url = "https://ballotpedia.org/Largest_cities_in_the_United_States_by_population"
    page_text = make_url_request_using_cache(page_url, CACHE_DICT)
    soup = BeautifulSoup(page_text, "html.parser")

    table = soup.find('table', attrs = {'class': 'marqueetable'})
    table_rows = table.find_all('tr')
    for tr in table_rows:
        td = tr.find_all('td')
        try:
            city_state_name = td[1].text
            rank = int(td[0].text)
            city_name = city_state_name.split(',')[0].strip()
            state_name = city_state_name.split(',')[1].strip()
            #city = City(cityName = city_name, rank = rank)
            cities[rank] = [city_name,state_name]
        except:
            pass
    print(cities)
    return cities


#Create a database
def create_db():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    #create City table
    drop_city = '''
        DROP TABLE IF EXISTS "City";
    '''
    cur.execute(drop_city)
    conn.commit()
    
    create_city = '''
        CREATE TABLE IF NOT EXISTS "City" (
            "Id"        INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "CityName"  TEXT NOT NULL,
            "StateName" TEXT NOT NULL,
        );
    '''
    cur.execute(create_city)
    conn.commit()

    # drop_Yelp = '''
    #     DROP TABLE IF EXISTS "Yelp";
    # '''
    # cur.execute(drop_Yelp)
    # conn.commit()
    conn.close()
#add City data
def insert_data():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    insert_city = '''
        INSERT INTO City
        VALUES (NULL, ?, ?);
    '''
    cities = get_city_names()
    for rank in cities.keys():
        cur.execute(insert_city, cities[rank])
    conn.commit()
    conn.close()



#Flask
# welcome.html
@app.route('/')
def welcome():
    return render_template('welcome.html')
# number -> city
@app.route('/<number>')
def show_city_name(number):
    cities = get_city_names()
    city_name = cities[number]
    html = render_template('number.html' , number = number, city_name = city_name )
    return html





if __name__ == "__main__":
    create_db()

    app.run(debug=True)