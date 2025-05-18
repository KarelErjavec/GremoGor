import requests

def get_highest_mountains(country_id):
    # SPARQL query to get the highest mountains in a specific country
    query = f"""
    SELECT ?mountain ?mountainLabel ?height WHERE {{
      ?mountain wdt:P31 wd:Q8502;  # instance of mountain
                wdt:P2044 ?height;  # height in meters
                wdt:P17 wd:{country_id}.  # located in the country
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    ORDER BY DESC(?height)
    LIMIT 10
    """

    url = "https://query.wikidata.org/sparql"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, params={'query': query, 'format': 'json'}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        mountains = []
        for item in data['results']['bindings']:
            mountains.append(item['mountainLabel']['value'])
        return mountains
    else:
        print("Error:", response.status_code)
        return None

# countryid
print(get_highest_mountains("Q215"))