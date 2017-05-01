import os
from requests import post
from json import dumps
from craigslist import CraigslistHousing
from filter_sets import filter_sets
import pymongo


SLACK_URL = os.environ['SLACK_URL']
MONGO_HOST = os.environ['MONGO_HOST']
MONGO_PORT = int(os.environ['MONGO_PORT'])
MONGO_COLLECTION = os.environ['MONGO_COLLECTION']

client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
db = client.craigslist
collection = getattr(db, MONGO_COLLECTION)

for name, filter_set in filter_sets.items():
    cl = CraigslistHousing(
        site='sfbay',
        area='sfc',
        category='apa',
        filters=filter_set,
    )

    results = list(cl.get_results(sort_by='newest', geotagged=True, limit=10))

    for result in results:
        db_key = {'id': result['id']}
        existing = collection.find_one(db_key)
        if not existing:
            data = {
                'text': '{}\n{}: {}\n{}'.format(
                    name,
                    result['price'],
                    result['name'],
                    result['url'],
                ),
            }
            response = post(
                SLACK_URL,
                data=dumps(data),
                headers={'Content-Type': 'application/json'},
            )
        collection.update(db_key, result, True)
