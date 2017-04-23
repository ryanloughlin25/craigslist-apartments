from requests import post
from json import dumps
from craigslist import CraigslistHousing
from filter_sets import filter_sets
import pymongo


url = 'https://hooks.slack.com/services/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'
client = pymongo.MongoClient('localhost', 27017)
db = client.craigslist

for name, filter_set in filter_sets.items():
    cl = CraigslistHousing(
        site='sfbay',
        area='sfc',
        category='apa',
        filters=filter_set,
    )

    results = list(cl.get_results(sort_by='newest', geotagged=True, limit=1))

    for result in results:
        db_key = {'id': result['id']}
        existing = db.apartments.find_one(db_key)
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
                url,
                data=dumps(data),
                headers={'Content-Type': 'application/json'},
            )
        db.apartments.update(db_key, result, True)
