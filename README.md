# Spotify playlist updater
I made a python program which scrapes Billboards TOP-100 chart every week and updates my playlist automatically

## Working

I built a scrapper which scrapes the data off the given URL (billboards.com/hot-100) and feeds the data to the main program which accesses the spotiy account via 'api.spotify' services and creates and adds tracks to the playlist accordingly

## Install

Install the necessary Python packages by running:

`$ pip install -r requirements.txt`

## Run

Run the entry-point script and follow the console instructions:

`$ python main.py`
