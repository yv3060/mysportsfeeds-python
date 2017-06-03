import os
import csv
import requests
from datetime import datetime
import simplejson as json
import platform
import base64

import ohmysportsfeedspy


# API class for dealing with v1.0 of the API
class API_v1_0(object):

    # Constructor
    def __init__(self, verbose, store_type=None, store_location=None):
        self.base_url = "https://www.mysportsfeeds.com/api/feed/pull"
        self.headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'MySportsFeeds Python/{} ({})'.format(ohmysportsfeedspy.__version__, platform.platform())
        }

        self.verbose = verbose
        self.store_type = store_type
        self.store_location = store_location

        self.valid_feeds = [
            'current_season',
            'cumulative_player_stats',
            'full_game_schedule',
            'daily_game_schedule',
            'daily_player_stats',
            'game_playbyplay',
            'game_boxscore',
            'scoreboard',
            'player_gamelogs',
            'team_gamelogs',
            'roster_players',
            'game_startinglineup',
            'active_players',
            'player_injuries',
            'latest_updates',
            'daily_dfs'
        ]

    # Verify a feed
    def __verify_feed_name(self, feed):
        is_valid = False

        for value in self.valid_feeds:
            if value == feed:
                is_valid = True
                break

        return is_valid

    ###
    ### Feed methods start here
    ###

    # Feed URL (with only a league specified)
    def __league_only_url(self, league, feed, output_format, params):
        return "{base_url}/{league}/{feed}.{output}".format(base_url=self.base_url, feed=feed, league=league, output=output_format)

    # Feed URL (with league + season specified)
    def __league_and_season_url(self, league, season, feed, output_format, params):
        return "{base_url}/{league}/{season}/{feed}.{output}".format(base_url=self.base_url, feed=feed, league=league, season=season, output=output_format)

    ###
    ### Feed methods end here
    ###

    # Indicate this version does support BASIC auth
    def supports_basic_auth(self):
        return True

    # Establish BASIC auth credentials
    def set_auth_credentials(self, username, password):
        self.auth = (username, password)
        self.headers['Authorization'] = 'Basic ' + base64.b64encode('{}:{}'.format(username,password).encode('utf-8')).decode('ascii')

    # Request data (and store it if applicable)
    def get_data(self, **kwargs):
        if not self.auth:
            raise AssertionError("You must authenticate() before making requests.")

        # establish defaults for all variables
        league = ""
        season = ""
        feed = ""
        output_format = ""
        params = {}

        # iterate over args and assign vars
        for key, value in kwargs.items():
            if str(key) == 'league':
                league = value
            elif str(key) == 'season':
                season = value
            elif str(key) == 'feed':
                feed = value
            elif str(key) == 'format':
                output_format = value
            else:
                params[key] = value

        # add force=false parameter (helps prevent unnecessary bandwidth use)
        params['force'] = 'true'

        if self.__verify_feed_name(feed) == False:
            raise ValueError("Unknown feed '" + feed + "'.")

        if feed == 'current_season':
            url = self.__league_only_url(league, feed, output_format, params)
        else:
            url = self.__league_and_season_url(league, season, feed, output_format, params)

        if self.verbose:
            print("Making API request to '{}'.".format(url))
            print("  with headers:")
            print(self.headers)
            print(" and params:")
            print(params)

        r = requests.get(url, params=params, headers=self.headers)

        if r.status_code == 200:
            if self.store_type != None:
                self.save_feed(r)

            if output_format == "json":
                data = json.loads(r.content)
            elif output_format == "xml":
                data = str(r.content)
            else:
                data = r.content.splitlines()

        elif r.status_code == 304:
            #print "Data has not changed since last call"
            filename = self.make_output_filename()

            with open(self.store_location + filename) as f:
                if output_format == "json":
                    data = json.load(f)
                elif output_format == "xml":
                    data = str(f.readlines()[0])
                else:
                    data = f.read().splitlines()

        else:
            raise Warning("API call failed with error: {error}".format(error=r.status_code))

        return data

    def make_output_filename(self):
        season = self.parse_season_type(self.season, self.season_type)

        s = ""
        for param in self.config.version_inputs["optional_params"]:
            if self.config.params.get(param):
                s += "-" + str(self.config.params.get(param))

        filename = "{sport}-{feed}-{date}-{season}{s}.{output_type}".format(sport=self.sport.lower(), feed=self.extension,
                                                                            date=self.config.params["fordate"],
                                                                            season=season, s=s,
                                                                            output_type=self.output_type)
        return filename

    def save_feed(self, response):
        # Save to memory regardless of selected method
        if self.output_type.lower() == "json":
            self.store.output = response.json()
        elif self.output_type.lower() == "xml":
            self.store.output = response.text
        elif self.output_type.lower() == "csv":
            self.store.output = response.content.split('\n')
        else:
            raise AssertionError("Requested output type incorrect.  Check self.output_type")

        if self.store.method == "standard":
            if not os.path.isdir("results"):
                os.mkdir("results")

            filename = self.make_output_filename()

            with open(self.store.location + filename, "w") as outfile:
                if isinstance(self.store.output, dict):  # This is JSON
                    json.dump(self.store.output, outfile)

                elif isinstance(self.store.output, unicode):  # This is xml
                    outfile.write(self.store.output.encode("u tf-8"))

                elif isinstance(self.store.output, list):  # This is csv
                    writer = csv.writer(outfile)
                    for row in self.store.output:
                        writer.writerow([row])

                else:
                    raise AssertionError("Could not interpret feed output format")

        elif self.store.method == "memory":
            pass  # Data already stored in store.output

        else:
            pass
