import re
import os
import sys
import bs4
import json
import yaml
import requests

def main():
    CITY = sys.argv[1].lower().replace(' ', '-')

    # Open json for city
    print('Loading ' + CITY + '.json')
    with open('cities/' + CITY + '.json') as json_data:
    	hotels_json = json.load(json_data)
    num_hotels = hotels_json['length']
    hotels = hotels_json['hotels']

    # Create city folder if doesn't exist
    if not os.path.exists('hotels/' + CITY):
    	os.makedirs('hotels/' + CITY)

    for hotel in hotels:

        name = hotel['name']
        url = hotel['link']

        HOTEL_NAME = name.lower().replace('/', ' ').replace(' ', '-')
        # Check that json file for this hotel doesn't already exist
        if not os.path.isfile('hotels/' + CITY + '/' + HOTEL_NAME + '.json'):

            print('Parsing', name)
            print(url)

            # Get request
            resp = requests.get(url)

            if resp.status_code == 200:
                # Make some soup
                soup = bs4.BeautifulSoup(resp.text, 'html.parser')
                # Extract params variable, and make it YAML friendly
                script = '{' + str(soup.find(id='property-page-params-init').string).split('{', 1)[1]
                # Only ASCII allowed
                script = re.sub(r'[^\x00-\x7F]+',' ', script.replace(':', ': '))
                # Load into dict
                params = yaml.load(script)

                hotelId = params['hotelId']

                # Basic info
                hotelInfo = params['hotelInfo']
                name = hotelInfo['englishName']
                stars = hotelInfo['starRating']['icon'].split('-')[-1]
                score = ''
                if 'score' in params['reviews']:
                    score = params['reviews']['score']
                address = hotelInfo['address']['full']
                rooms = []
                nearbyPropertiesList = []
                longitude = soup.find('meta', property="og:longitude")['content']
                latitude = soup.find('meta', property="og:latitude")['content']
                cityName = soup.find('meta', property="og:locality")['content']
                countryName = soup.find('meta', property="og:country-name")['content']

                # Room info
                if 'masterRoomInfo' in params:
                    for room in params['masterRoomInfo']:
                        facilityGroups = {}
                        if 'facilityGroups' in room:
                            for facilityGroup in room['facilityGroups']:
                                facilityGroupName = facilityGroup['name']
                                facilities = []
                                for facility in facilityGroup['facilities']:
                                    facilities.append(facility['title'])
                                facilityGroups[facilityGroupName] = facilities
                        rooms.append({'id': room['id'], 'name': room['name'], 'facilities': facilityGroups})
                
                # Nearby locations
                if 'essentialInfo' in params:
                    essentialInfo = params['essentialInfo']
                    if 'nearbyProperties' in essentialInfo:
                        nearbyProperties = essentialInfo['nearbyProperties']
                        nearbyPropertiesList = [{'categoryName': properties['categoryName'], 'places': properties['places']} for properties in nearbyProperties]



                hotelDescription = ''
                hotelUsefulInfo = ''
                hotelFeatureGroups = []

                resp2 = requests.get("https://www.agoda.com/api/en-us/Hotel/AboutHotel?hotelId=" + str(hotelId))
                script2 = resp2.text
                params2 = json.loads(script2)
                
                if params2['HotelDesc']:
                    hotelDescription = params2['HotelDesc']['Overview'].replace(r'[<BR>\n]+', ' ')
                if 'UsefulInfoGroups' in params2:
                    hotelUsefulInfo = [
                        {
                            'Name':x['Name'],
                            'Items':[
                                {
                                    'Title':y['Title'].replace('\n', ''),
                                    'Description':y['Description']
                                } for y in x['Items']]
                        } for x in params2['UsefulInfoGroups']]
                if 'FeatureGroups' in params2:
                    for featureGroup in params2['FeatureGroups']:
                        features = []
                        for item in featureGroup['Feature']:
                            features.append(item['Name'])
                        hotelFeatureGroups.append({featureGroup['Name']:features})
                
                # Create dictionary
                hoteldict = {
                                'country':countryName,
                                'city':cityName,
                                'longitude':longitude,
                                'latitude':latitude,
                                'name':name,
                                'stars':stars,
                                'address':address,
                                'url':url,
                                'hotelId':hotelId,
                                'hotelDesc':hotelDescription,
                                'usefulInfo':hotelUsefulInfo,
                                'features':hotelFeatureGroups,
                                'rooms':rooms,
                                'nearbyProperties':nearbyPropertiesList
                            }

                # Save json for hotel
                with open('hotels/' + CITY + '/' + HOTEL_NAME + '.json', 'w') as f:
                    json.dump(hoteldict, f)
                    print('JSON saved')
            else:
                print('Page for', name, 'not found')
        # If json exists, skip
        else:
            print('JSON for', name, 'already exists, skipping.')
if __name__ == '__main__':
    main()