import os
import boto3
from requests import post
from json import dumps, loads
from craigslist import CraigslistHousing
from filter_sets import filter_sets
from operator import itemgetter


SLACK_URL = os.environ['SLACK_URL']


def post_to_slack(name, result):
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


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    previous_apartments = loads(
        s3.get_object(
            Bucket='ryan-loughlin-craigslist',
            Key='dev_apartments.json',
        )['Body'].read()
    )

    for name, filter_set in filter_sets.items():
        cl = CraigslistHousing(
            site='sfbay',
            area='sfc',
            category='apa',
            filters=filter_set,
        )

        results = list(cl.get_results(sort_by='newest', geotagged=True, limit=100))

        for result in results:
            try:
                index = list(map(itemgetter('id'), previous_apartments)).index(result['id'])
                previous_apartments[index] = result
            except ValueError as e:
                previous_apartments.append(result)
                post_to_slack(name, result)

    s3.put_object(
        Bucket='ryan-loughlin-craigslist',
        Key='dev_apartments.json',
        Body=dumps(previous_apartments),
    )


if __name__ == '__main__':
    lambda_handler(None, None)
