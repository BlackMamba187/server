from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

from utilities.scrape import get_active_teams, get_team_info, get_all_players_data, get_all_players_data_for_all_letters, get_player_data, get_season_avgs

app = Flask(__name__)
CORS(app)

cache = {}

def update_cache():
    try:
        cache['active_teams'] = get_active_teams()
    except Exception as e:
        print(f"Failed to update active_teams: {e}")

    try:
        cache['team_info'] = {team_id: get_team_info(team_id) for team_id in cache.get('active_teams', {})}
    except Exception as e:
        print(f"Failed to update team_info: {e}")

    try:
        cache['all_players_data'] = get_all_players_data_for_all_letters()
    except Exception as e:
        print(f"Failed to update all_players_data: {e}")

    try:
        cache['season_avgs'] = get_season_avgs()
    except Exception as e:
        print(f"Failed to update season_avgs: {e}")

    try:
        cache['player_data'] = {player_id: get_player_data(player_id) for player_id in cache.get('all_players_data', {})}
    except Exception as e:
        print(f"Failed to update player_data: {e}")

scheduler = BackgroundScheduler()
job = scheduler.add_job(func=update_cache, trigger="interval", hours=1)
scheduler.start()

# Manually update the cache once right at the start
update_cache()

def get_data_or_info_when_next(key):
    data = cache.get(key)
    if data is None:
        return jsonify({'message': 'Data not available in cache'}), 202
    return data

@app.route('/', methods=['GET'])
def home():
    return "Welcome to our nba web service!"

@app.route('/seasonavg', methods=['GET'])
def season_avg():
    return get_data_or_info_when_next('season_avgs')

@app.route('/activeteams', methods=['GET'])
def active_teams_json():
    return get_data_or_info_when_next('active_teams')

@app.route('/team/<team_id>', methods=['GET'])
def get_team_info_json(team_id):
    data = cache.get('team_info', {}).get(team_id)
    return data if data else jsonify({'message': 'Team not found'}), 404

@app.route('/players/', methods=['GET'])
def get_all_players_data_for_all_letters_json():
    return get_data_or_info_when_next('all_players_data')

@app.route('/player/<player_id>', methods=['GET'])
def get_player_data_json(player_id):
    data = cache.get('player_data', {}).get(player_id)
    return data if data else jsonify({'message': 'Player not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
