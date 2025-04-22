import flask
from flask import request, jsonify,render_template
import threading
import time


from server.api import api_router,games

app = flask.Flask(__name__)
app.register_blueprint(api_router)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/waiting/<game_id>')
def waiting_room(game_id):
    return render_template('waiting_room.html', game_id=game_id)

@app.route('/game/<game_id>')
def game_page(game_id):
    return render_template('game.html', game_id=game_id)

def runing_game():
    while True:
        for game_id, engine in list(games.items()):
            if engine is not None:
                try:
                    engine.process_turn()
                    if engine.is_game_end():
                        print(f"Game {game_id} has ended.")
                        # del games[game_id]
                except Exception as e:
                    print(f"Error processing turn for game {game_id}: {e}")
        time.sleep(1)

# set the game processing thread
game_main_thread = threading.Thread(target=runing_game, daemon=True)

if __name__ == "__main__":
    game_main_thread.start()
    app.run(debug=True, port=5000)