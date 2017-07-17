import requests
import json
import bs4
import sys
import os

def main():
    HOST = 'https://www.agoda.com'
    CITY = sys.argv[1].lower().replace(' ', '-')
    URL = HOST + '/destination/city/' + CITY + '-vn.html'

    print(' '.join(('Parsing', sys.argv[1], 'hotels')))
    print(URL)
    
    resp = requests.get(URL)
    AgodaSoup = bs4.BeautifulSoup(resp.text, 'html.parser')

    hotels = []
    sections = ['5stars-hotels', '4stars-hotels', '3stars-hotels', 'cheap-hotels']
    for section in sections:
        a_tags = AgodaSoup.find(id=section).find_all('a')
        for a_tag in a_tags:
            name = a_tag.string
            href = a_tag.get('href').split('?')[0]
            parts = href.split('/')
            if len(parts) == 4 and parts[0] == '' and parts[1] != '' and parts[2] == 'hotel' and parts[3] == CITY + '-vn.html':
                hotels.append((name, HOST + href))

    keys = ('name', 'link')
    hotels_json = list(dict(zip(keys, hotel)) for hotel in hotels)
    complete_json = {"length": len(hotels), "hotels": hotels_json}
    print('Saving json...')
    
    
    directory = 'hotels/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    directory2 = 'cities/'
    if not os.path.exists(directory2):
        os.makedirs(directory2)
    
    with open('cities/' + CITY + '.json', 'w') as f:
        json.dump(complete_json, f)
    print('Done')


if __name__ == '__main__':
    main()