from requests import post
from json import dumps
from craigslist import CraigslistHousing


url = 'https://hooks.slack.com/services/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'

filters = {'max_price': 3500, 'min_price': 2000, 'bedrooms': 2, 'zip_code': 94118}
cl = CraigslistHousing(
    site='sfbay',
    area='sfc',
    category='apa',
    filters=filters,
)

results = list(cl.get_results(sort_by='newest', geotagged=True, limit=1))
for result in results:
    data = {
        'text': '{}: {}\n{}'.format(
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
