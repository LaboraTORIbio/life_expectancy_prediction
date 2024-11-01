import json
import requests


country_data = {'country': 'Afghanistan',
 'year': 2015,
 'status': 'Developing',
 'adult_mortality': 263.0,
 'infant_deaths': 62,
 'alcohol': 0.01,
 'percentage_expenditure': 71.27962362,
 'hepatitis_b': 65.0,
 'measles': 1154,
 'bmi': 19.1,
 'under-five_deaths': 83,
 'polio': 6.0,
 'total_expenditure': 8.16,
 'diphtheria': 65.0,
 'hiv_aids': 0.1,
 'gdp': 584.25921,
 'population': 33736494.0,
 'thinness_10-19_years': 17.2,
 'thinness_5-9_years': 17.3,
 'income_composition_of_resources': 0.479,
 'schooling': 10.1,
 'infant_mortality_rate': 54.5873152241597,
 'neonatal_mortality_rate': 42.3639686983098,
 'under-five_mortality_rate': 72.6769805471922}

url = 'http://localhost:9696/predict'
response = requests.post(url, json=country_data)
result = response.json()
print(f"The predicted life expectancy is {result['life_expectancy']} years.")