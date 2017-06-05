# MySportsFeeds Wrapper - Python

##Instructions

Clone repo, install requirements and run tests
    
    $ git clone https://github.com/MySportsFeeds/mysportsfeeds-python.git
    $ make build

OR

Use PIP install
    
    $ pip install ohmysportsfeedspy

If you haven't signed up for API access, do so here [https://www.mysportsfeeds.com/index.php/register/](https://www.mysportsfeeds.com/index.php/register/)

##Usage

Create main MySportsFeeds object with API version as input parameter

    from ohmysportsfeedspy import MySportsFeeds

    msf = MySportsFeeds(version="1.0")

Authenticate (v1.0 uses your MySportsFeeds account credentials)

    msf.authenticate("YOUR_USERNAME", "YOUR_PASSWORD")

Start making requests, specifying: league, season, feed, format, and any other applicable params for the feed

    output = msf.msf_get_data(league='nba',season='2016-2017-regular',feed='player_gamelogs',format='json',player='stephen-curry')
    output = msf.msf_get_data(league='nfl',season='2015-2016-regular',feed='cumulative_player_stats',format='xml',team='dallas-cowboys')
    output = msf.msf_get_data(league='mlb',season='2016-playoff',feed='full_game_schedule',format='csv')

That's it!  Returned data is also stored locally under "results/" by default, in appropriately named files.
