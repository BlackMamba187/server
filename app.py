from flask import Flask, jsonify, make_response, request
from nba_api.stats.static import players, teams
import nba_api.stats.static.teams as nba_teams
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

@app.route('/team/<teamId>/players', methods=['GET'])
def get_team_players(teamId):
    player_dict = players.get_active_players()
    team_players = []

    for player in player_dict:
        player_id = player['id']
        career = playercareerstats.PlayerCareerStats(player_id=player_id).get_data_frames()[0]
        # Check if the player played in the latest season and for the required team
        if not career.empty and str(career['TEAM_ID'].iloc[-1]) == teamId:
            team_players.append(player)

    return jsonify(team_players)

if __name__ == '__main__':
    app.run(debug=True)
