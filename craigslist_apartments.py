import os
import boto3
import botocore
from requests import post
from json import dumps, loads
from craigslist import CraigslistHousing
from filter_sets import filter_sets
from operator import itemgetter


SLACK_URL = os.environ['SLACK_URL']
S3_BUCKET = os.environ['S3_BUCKET']
S3_KEY = os.environ['S3_KEY']
RESULTS_PER_FILTER = int(os.environ['RESULTS_PER_FILTER'])


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


def get_previous_apartments():
    s3 = boto3.client('s3')
    try:
        return loads(
            s3.get_object(
                Bucket=S3_BUCKET,
                Key=S3_KEY,
            )['Body'].read()
        )
    except botocore.errorfactory.ClientError as client_error:
        if client_error.response['Error']['Code'] == 'NoSuchKey':
            return []
        else:
            raise


def put_apartments(apartments):
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=S3_KEY,
        Body=dumps(apartments),
    )


def lambda_handler(event, context):
    apartments = get_previous_apartments()

    for name, filter_set in filter_sets.items():
        cl = CraigslistHousing(
            site='sfbay',
            area='sfc',
            category='apa',
            filters=filter_set,
        )

        results = list(
                cl.get_results(
                    sort_by='newest',
                    geotagged=True,
                    limit=RESULTS_PER_FILTER,
                )
            )

        for result in results:
            try:
                # update previously seen apartment listing
                apartment_ids = map(itemgetter('id'), apartments)
                index = list(apartment_ids).index(result['id'])
                apartments[index] = result
            except ValueError as e:
                # post new apartment listing
                apartments.append(result)
                post_to_slack(name, result)

    put_apartments(apartments)


if __name__ == '__main__':
    lambda_handler(None, None)
