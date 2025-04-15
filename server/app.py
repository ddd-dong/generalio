import flask
from flask import request, jsonify,render_template

from server.api import api_router

app = flask.Flask(__name__)
app.register_blueprint(api_router, url_prefix='/api')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/game/<game_id>')
def game(game_id):
    return render_template('game.html', game_id=game_id)




if __name__ == "__main__":
    app.run(debug=True, port=5000)