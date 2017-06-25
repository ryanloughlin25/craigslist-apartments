WORKING_DIRECTORY=$(pwd)
zip -9 $WORKING_DIRECTORY/$1 craigslist_apartments.py filter_sets.py
cd env/lib/python3.6/site-packages
zip -rg $WORKING_DIRECTORY/$1 *
