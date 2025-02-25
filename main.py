import datetime
import json
import logging
import os

import httpx
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


## load envar -------------------------------------------------------
load_dotenv()
HH_COUNT_JSON_PATH = os.getenv('HH_COUNT_JSON_PATH')

## constants --------------------------------------------------------
ITEMS_URL: str = (
    'https://repository.library.brown.edu/api/search/?q=rel_is_member_of_collection_ssim:%22bdr:wum3gm43%22&rows=0'
)
ORG_URL: str = 'https://repository.library.brown.edu/api/search/?q=-rel_is_part_of_ssim:*+rel_is_member_of_collection_ssim:%22bdr:wum3gm43%22&rows=0'
START_OF_YEAR: datetime = datetime.datetime(2025, 1, 6)
START_OF_YEAR_COUNT: int = 200_000
TOTAL_TARGET_COUNT = 900_000

## grap api data ----------------------------------------------------
items_jdict: dict = httpx.get(ITEMS_URL).json()
orgs_jdict: dict = httpx.get(ORG_URL).json()

## extract counts ---------------------------------------------------
items_count: int = items_jdict['response']['numFound']
orgs_count: int = orgs_jdict['response']['numFound']

## calculate days since first working day of 2025 -------------------
current_date: datetime = datetime.datetime.now()
days_elapsed: int = (current_date - START_OF_YEAR).days
log.info(f'days elapsed: ``{days_elapsed}``')

## calculate items processed per day -------------------------------
items_ingested_this_year: int = items_count - START_OF_YEAR_COUNT
log.info(f'items_ingested_this_year: ``{items_ingested_this_year}``')
items_per_day_since_year_start: float = items_ingested_this_year / days_elapsed
log.info(f'items_per_day_since_year_start: ``{items_per_day_since_year_start}``')

## predict completion date for remaining items ----------------------
number_of_items_remaining_to_ingest: int = TOTAL_TARGET_COUNT - (START_OF_YEAR_COUNT + items_ingested_this_year)
log.info(f'number_of_items_remaining_to_ingest: ``{number_of_items_remaining_to_ingest}``')
days_to_target: int = number_of_items_remaining_to_ingest / items_per_day_since_year_start
log.info(f'days to target: ``{days_to_target}``')
target_date: datetime.date = current_date + datetime.timedelta(days=days_to_target)
log.info(
    f'Predicted completion date for remaining ``{number_of_items_remaining_to_ingest}`` items: {target_date.strftime("%Y-%m-%d")}'
)

## prep json --------------------------------------------------------
data: dict = {
    '_meta_': {
        'data_prepared_date': str(datetime.datetime.now()),
        'assumptions': {
            'start_of_year_count': START_OF_YEAR_COUNT,
            'total_items_count': TOTAL_TARGET_COUNT,
        },
        'days_elapsed_since_2025-Jan-06': days_elapsed,
        'items_ingested_this_year': items_ingested_this_year,
        'items_per_day_since_year_start': items_per_day_since_year_start,
        'number_of_items_remaining_to_ingest': number_of_items_remaining_to_ingest,
    },
    'items_count': items_count,
    'orgs_count': orgs_count,
    'expected_completion_date': target_date.strftime('%Y-%m-%d'),
}
json_data: str = json.dumps(data, indent=2, sort_keys=True)

## save and output --------------------------------------------------
if HH_COUNT_JSON_PATH:
    with open(HH_COUNT_JSON_PATH, 'w') as f:
        f.write(json_data)
log.info(f'json_data: ``{json_data}``')

## eof
