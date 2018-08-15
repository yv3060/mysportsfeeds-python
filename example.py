from ohmysportsfeedspy import MySportsFeeds

Data_query = MySportsFeeds('1.2',verbose=True)
Data_query.authenticate('7f38bf2c-0bb5-4308-85b0-6057b8', 'Dk30RQHT')
Output = Data_query.msf_get_data(league='nba',season='2016-2017-regular',feed='player_gamelogs',format='json',player='stephen-curry')

print(Output)
