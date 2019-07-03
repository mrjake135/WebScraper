# WebScraper
Webscraper used to parse agoda hotels

Currently only works for Vietnamese cities.
Use no.9 to scrape a list of hotels by executing on terminal python 9.py "city_name". This will produce a json file with all the hotels
within a certain Vietnamese city. The list of hotels is from Agoda.com.

Use no.10 to parse the list of hotels and create a json file with a dictionary of information. This information comes from Agoda.com.

This webscraper does NOT use a API, rather, it simply scrapes the individual elements of each page, which is why it takes so long but also has so much information
