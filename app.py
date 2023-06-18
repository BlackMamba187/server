from flask import Flask, jsonify
from flask_cors import CORS
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import commonplayerinfo

app = Flask(__name__)
CORS(app)

@app.route('/players', methods=['GET'])
def get_players():
    player_dict = players.get_players()
    return jsonify(player_dict)

@app.route('/team/<teamId>', methods=['GET'])
def team_profile(teamId):
    team = teams.find_team_name_by_id(teamId)
    if team:
        return jsonify(team)
    else:
        return jsonify({'message': 'Team not found'}), 404

@app.route('/teams', methods=['GET'])
def get_teams():
    teams = teams.get_teams()
    return jsonify(teams)

if __name__ == '__main__':
    app.run(debug=True)
