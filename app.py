from flask import Flask
from flask_cors import CORS

from utilities.scrape import get_active_teams, get_team_info, get_all_players_data, get_all_players_data_for_all_letters,  get_player_data

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "Welcome to our web service!"
    
@app.route('/activeteams', methods=['GET'])
def active_teams_json():
    data = get_active_teams()
    return data


@app.route('/team/<team_id>', methods=['GET'])
def get_team_info_json(team_id):
    data = get_team_info(team_id)
    return data


@app.route('/players/', methods=['GET'])
def get_all_players_data_for_all_letters_json():
    data = get_all_players_data_for_all_letters()
    return data


@app.route('/player/<player_id>', methods=['GET'])
def get_player_data_json(player_id):
    data = get_player_data(player_id)
    return data


if __name__ == '__main__':
    app.run(debug=True)
