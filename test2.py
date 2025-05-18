import requests

def get_country_id_by_name(country_name):
    # Prepare the SPARQL query with the country name
    query = f"""
    SELECT ?country ?countryLabel WHERE {{
      ?country wdt:P31 wd:Q6256;  # instance of country
               rdfs:label ?countryLabel.
      FILTER(CONTAINS(LCASE(?countryLabel), "{country_name.lower()}"))  # search for the country name
      FILTER(LANG(?countryLabel) = "en")  # ensure the label is in English
    }}
    """

    url = "https://query.wikidata.org/sparql"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, params={'query': query, 'format': 'json'}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        countries = []
        for item in data['results']['bindings']:
            countries.append({
                'id': item['country']['value'],
                'name': item['countryLabel']['value']
            })
        return countries
    else:
        print("Error:", response.status_code)
        return None

# Example usage: Search for a country ID by name
country_name = "Slovenia"  # Replace with the desired country name
print(get_country_id_by_name(country_name))