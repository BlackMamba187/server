from flask import Flask, jsonify, make_response, request
from nba_api.stats.static import players, teams
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/players', methods=['GET'])
def get_players():
    player_dict = players.get_players()
    return jsonify(player_dict)

@app.route('/teams', methods=['GET'])
def get_teams():
    team_dict = teams.get_teams()
    return jsonify(team_dict)

if __name__ == '__main__':
    app.run(debug=True)
