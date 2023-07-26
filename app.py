from flask import Flask
from flask_cors import CORS
from flask_caching import Cache

from utilities.scrape import (get_active_teams, get_team_info, get_all_players_data, get_all_players_data_for_all_letters,
                              get_player_data, get_season_avgs)

app = Flask(__name__)
CORS(app)

# Set up Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/', methods=['GET'])
def home():
    return "Welcome to our nba web service!"

@app.route('/seasonavg', methods=['GET'])
@cache.cached(timeout=86400) # data updates once a day
def season_avg():
    data = get_season_avgs()
    return data
    
@app.route('/activeteams', methods=['GET'])
@cache.memoize() # data never updates
def active_teams_json():
    data = get_active_teams()
    return data

@app.route('/team/<team_id>', methods=['GET'])
@cache.cached(timeout=86400) # data updates once a day
def get_team_info_json(team_id):
    data = get_team_info(team_id)
    return data

@app.route('/players/', methods=['GET'])
@cache.memoize() # data never updates
def get_all_players_data_for_all_letters_json():
    data = get_all_players_data_for_all_letters()
    return data

@app.route('/player/<player_id>', methods=['GET'])
@cache.cached(timeout=86400) # data updates once a day
def get_player_data_json(player_id):
    data = get_player_data(player_id)
    return data

if __name__ == '__main__':
    app.run(debug=True)
