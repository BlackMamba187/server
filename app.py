from flask import Flask, jsonify, make_response, request
from nba_api.stats.static import players, teams
import nba_api.stats.static.teams as nba_teams
from nba_api.stats.endpoints import teamdetails
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/players', methods=['GET'])
def get_players():
    player_dict = players.get_players()
    return jsonify(player_dict)

@app.route('/team/<teamId>', methods=['GET'])
def team_profile(teamId):
    team = nba_teams.find_team_name_by_id(teamId)
    if team:
        return jsonify(team)
    else:
        return jsonify({'message': 'Team not found'}), 404

@app.route('/teams', methods=['GET'])
def teams():
    teams = nba_teams.get_teams()
    return jsonify(teams)

@app.route('/teamdetails/<teamId>', methods=['GET'])
def get_team_details(teamId):
    details = teamdetails.TeamDetails(teamId)
    return jsonify(details)

if __name__ == '__main__':
    app.run(debug=True)
