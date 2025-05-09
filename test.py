import requests
#začasna datoteka
def get_mountain_info(mountain_name):
    # Search 
    search_url = "https://www.wikidata.org/w/api.php"
    search_params = {
        'action': 'wbsearchentities',
        'search': mountain_name,
        'language': 'si',
        'format': 'json'
    }
 
    search_response = requests.get(search_url, params=search_params)
    search_data = search_response.json()
 
    if not search_data['search']:
        return
 
    # prvi rezultat
    mountain_entity = search_data['search'][0]
    mountain_id = mountain_entity['id']
 
    # Data request
    entity_url = "https://www.wikidata.org/w/api.php"
    entity_params = {
        'action': 'wbgetentities',
        'ids': mountain_id,
        'props': 'claims',
        'format': 'json'
    }
 
    entity_response = requests.get(entity_url, params=entity_params)
    entity_data = entity_response.json()
 
    # height (P2048), location (P625)
    claims = entity_data['entities'][mountain_id]['claims']
 
    height = claims.get('P2048', [])
    location = claims.get('P625', [])
    img = claims.get('P18', [])
 
    # mm - m
    if height:
        height_value = int(height[0]['mainsnak']['datavalue']['value']['amount']) / 1000
    else:
        height_value = None
 
    # lokacija
    if location:
        latitude = location[0]['mainsnak']['datavalue']['value']['latitude']
        longitude = location[0]['mainsnak']['datavalue']['value']['longitude']
        location_value = (latitude, longitude)
    else:
        location_value = None

    # img url
    if img: 
        print(f"https://commons.wikimedia.org/wiki/Special:FilePath/{img[0]['mainsnak']['datavalue']['value']}")

    else: img_value = none
 
    print({
        "mount" : mountain_name,
        "height" : height_value,
        "location" : location_value

    })

get_mountain_info('Triglav')