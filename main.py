import datetime
import json
import os

import requests
from dotenv import load_dotenv

## load envar
load_dotenv()
HH_COUNT_JSON_PATH = os.getenv('HH_COUNT_JSON_PATH')

## grap api data
items_url: str = (
    'https://repository.library.brown.edu/api/search/?q=rel_is_member_of_collection_ssim:%22bdr:wum3gm43%22&rows=0'
)
orgs_url: str = 'https://repository.library.brown.edu/api/search/?q=-rel_is_part_of_ssim:*+rel_is_member_of_collection_ssim:%22bdr:wum3gm43%22&rows=0'
items_jdict: dict = requests.get(items_url).json()
orgs_jdict: dict = requests.get(orgs_url).json()

## extract counts
items_count: int = items_jdict['response']['numFound']
orgs_count: int = orgs_jdict['response']['numFound']

## calculate days since first working day of 2025
start_date: datetime = datetime(2025, 1, 6)
current_date: datetime = datetime.now()
days_elapsed: int = (current_date - start_date).days

## calculate items processed per day
items_per_day: float = items_count / days_elapsed

## predict calendar date for when 700,000 items will be processed
target_items: int = 700_000
days_to_target: int = target_items / items_per_day
target_date: datetime = current_date + datetime.timedelta(days=days_to_target)
print(f'Predicted date for 700,000 items: {target_date.strftime("%Y-%m-%d")}')

## prep json
data: dict = {'items_count': items_count, 'orgs_count': orgs_count}
json_data: str = json.dumps(data, indent=2, sort_keys=True)

## save and output
if HH_COUNT_JSON_PATH:
    with open(HH_COUNT_JSON_PATH, 'w') as f:
        f.write(json_data)
print(json_data)

## eof
