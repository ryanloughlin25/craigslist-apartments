# goal
Scrape craigslist at regular intervals for apartment listings that match a given set of filters and post those apartment listings to slack.

# dependencies
python (3.6)
boto3
[python-craigslist](https://github.com/juliomalegria/python-craigslist)
aws s3

The code can be run locally (although it will still make requests to s3 and craigslist), but I recommend using an aws lambda function.  This should keep the compute costs in the free tier so that the only bill will be for storing previously seen apartment listings in s3.

# deployment
Instructions for building a lambda function can be found in the [aws docs](http://docs.aws.amazon.com/lambda/latest/dg/lambda-app.html).  I will describe my own process for deployment.  I chose to upload a zip to lambda because of the dependency on python-craigslist.

## filters
The filters are currently setup for 2 bedroom apartments in the Inner Richmond and Marina districts.  They are stored as dictionaries in `filters.py`.  Edit the filters based on your interests or you can deploy it as is to see what it does and come back to the filters later.  The python-craigslist README describes how to use a python interpreter to list the available filters.

## create a lambda deployment package (zip file)
1. Create a [virtual environment](https://virtualenv.pypa.io/en/stable/) called `env` in the root of the repository.
`virtualenv -p python3 env`
2. Source the virtual environment
`source env/bin/activate`
3. Install dependencies
`pip install -r requirements.txt`
4. Run `lambda_zip.sh`.  It expects 1 positional argument, which is the name of the zip file to create and it expects the virtualenv called `env` to exist.
`./lambda_zip.sh lambda_function.zip`

## create an incoming webhook for slack
slack has good docs for creating an [incoming webhook](https://api.slack.com/incoming-webhooks).

## create a lambda function in aws
aws has documentation for most of the process, I will comment on the parts specific to this project.

* Start by uploading the zip created by `lambda_zip.sh`.
* In the configuration tab, the runtime should be Python 3.6 and the Handler should be `craigslist_apartments.lambda_handler`.
* In Advanced settings (still in the configuration tab) set the timeout high enough to allow for multiple requests to craigslist and slack.  I used 2 minutes.

### required environment variables
* `SLACK_URL` - a url for an incoming webhooking in slack.
* `S3_BUCKET` - s3 bucket name.  Bucket must exist before running the code.
* `S3_KEY` - s3 key name
* `REQUESTS_PER_FILTER` - number of results to download from craigslist each time the code is executed.  It will download this many for each filter every time, but only post new ones to slack.  This means that if there are no new apartment listings since the last run, then it will download them and not post anything to slack.

### trigger
I recommend using a CloudWatch Events trigger to run at regular intervals.  The interval should be determined based on how frequently you want notifications, your apartment filters, and `REQUESTS_PER_FILTER`.

For example, I was looking for 2 bedroom apartments in each of 2 zip codes and I used `REQUESTS_PER_FILTER=100` and used a CloudWatch Events trigger rate of 1 hour.  I found that this was more than enough to post all apartment listings relevant to my filters.  Usually it would post 5 or less per hour.  But it did post 100 per filter the first time it ran, which can feel like a lot of spam.

# Thanks for reading
Please let me know if you encounter any issues.
