from flask import Blueprint, request, jsonify
import uuid 

from game.engine import GameEngine
from game.board import GameBoard
from game.player import Player_Info
from game.game_types import Direction
from server.utils import check_config
from utils.color import PLAYER_COLOR_LIST

api_router = Blueprint('api', __name__)
games = {} # game_id -> game_engine or None
users = {} # unique_id -> {"name": str, "game_id": gameid,"player_info" Player_Info}



@api_router.route('/api/create_user', methods=['POST'])
def create_user():
    """
    Create a new user with the given configuration.
    config format:
    {
        "name": str
    }
    """
    config = request.get_json()
    if not config:
        return jsonify({"error": "Invalid configuration"}), 400
    if not check_config(config, ['name']):
        return jsonify({"error": "Missing configuration key"}), 400
    
    unique_id = str(uuid.uuid4())
    if unique_id not in users:
        users[unique_id] = {
            "name": config['name'],
            "game_id": None,
            "player_info": None
        }
        return jsonify({"unique_id": unique_id}), 200
    else:
        return jsonify({"error": "Unique ID generation failed"}), 400


@api_router.route('/api/new_game', methods=['POST'])
def new_game():
    """
    Create a new game with the given configuration.
    config format:
    {
        "host_unique_id": str
    }
    """
    config = request.get_json()
    if not config:
        return jsonify({"error": "Invalid configuration"}), 400
    if not check_config(config, ['host_unique_id']):
        return jsonify({"error": "Missing configuration key"}), 400

    host_unique_id = config['host_unique_id']
    if host_unique_id not in users:
        return jsonify({"error": "Host unique ID not found"}), 400

    
    for _ in range(10):
        game_id = str(uuid.uuid4())[:6]
        if game_id not in games:
            break
    if game_id in games:
        return jsonify({"error": "Game ID generation failed"}), 400

    
    games[game_id] = None
    users[host_unique_id]['game_id'] = game_id
    users[host_unique_id]['player_info'] = None
    return jsonify({"game_id": game_id}), 200

@api_router.route('/api/join_game', methods=['POST'])
def join_game():
    """
    Join an existing game with the given configuration.
    config format:
    {
        "game_id": str,
        "unique_id": str
    }
    """
    config = request.get_json()
    if not config:
        return jsonify({"error": "Invalid configuration"}), 400
    if not check_config(config, ['game_id', 'unique_id']):
        return jsonify({"error": "Missing configuration key"}), 400

    game_id = config['game_id']
    unique_id = config['unique_id']

    if game_id not in games:
        return jsonify({"error": "Game ID not found"}), 400
    if unique_id not in users:
        return jsonify({"error": "Unique ID not found"}), 400
    
    if users[unique_id]['game_id'] is not None:
        return jsonify({"error": "User already in a game"}), 400

    users[unique_id]['game_id'] = game_id
    return jsonify({"message": "Joined game successfully"}), 200

@api_router.route('/api/start_game', methods=['POST'])
def start_game():
    """
    Start the game with the given configuration.
    config format:
    {
        "hoster_unique_id": str,
        "game_id": str,
        "game_config": {
            "width": int,
            "height": int,
            "players": [
                {
                    "name": str,
                    "unique_id": str
                 }],
            "optional":{
                "cities_fairness": float,
                "cities_circles_radius_ratio": float,
                "city_num": int,
                "mountain_density": float,
                "minimal_general_distance": int
            }
    }
    """
    recive_config = request.get_json()
    if not recive_config:
        return jsonify({"error": "Invalid configuration"}), 400
    if not check_config(recive_config, ['hoster_unique_id',"game_id", 'game_config']):
        return jsonify({"error": "Missing configuration key"}), 400
    if not check_config(recive_config['game_config'], ['width', 'height', 'players']):
        return jsonify({"error": "Missing configuration key"}), 400
    if recive_config['hoster_unique_id'] not in users:
        return jsonify({"error": "Host unique ID not found"}), 400
    if recive_config['game_id'] not in games:
        return jsonify({"error": "Game ID not found"}), 400
    if users[recive_config['hoster_unique_id']]['game_id'] != recive_config['game_id']:
        return jsonify({"error": "Host unique ID does not match game ID"}), 400
    if games[recive_config['game_id']] is not None:
        return jsonify({"error": "Game already started"}), 400
    if len(recive_config['game_config']['players']) < 2:
        return jsonify({"error": "Not enough players"}), 400
    players = []
    for i,player in enumerate(recive_config['game_config']['players']):
        if player['unique_id'] not in users:
            return jsonify({"error": "Player unique ID not found"}), 400
        if users[player['unique_id']]['game_id'] != recive_config['game_id']:
            return jsonify({"error": "Player unique ID does not match game ID"}), 400
        if users[player['unique_id']]['player_info'] is not None:
            return jsonify({"error": "Player already in a game"}), 400
        player_info = Player_Info(player['name'], i, player['unique_id'])
        player_info.color = PLAYER_COLOR_LIST[i%len(PLAYER_COLOR_LIST)]
        players.append(player_info)
        users[player['unique_id']]['player_info'] = player_info

    if recive_config['game_config']["optional"] is None:
        board = GameBoard(recive_config['game_config']['width'], recive_config['game_config']['height'], players)
    else:
        optional_config = recive_config['game_config']["optional"]
        optional_config_check_list = ['cities_fairness', 'cities_circles_radius_ratio', 'city_num', 'mountain_density', 'minimal_general_distance']
        for key in optional_config:
            if key not in optional_config_check_list:
                return jsonify({"error": f"Invalid optional configuration key: {key}"}), 400
        board = GameBoard(recive_config['game_config']['width'], recive_config['game_config']['height'], players, **optional_config)
    isvalied,message =  board.initialize_map()
    print(board)
    if isvalied == False:
        return jsonify({"error": message}), 400
    game_engine = GameEngine(board)
    games[recive_config['game_id']] = game_engine
    return jsonify({"isstart":True,"message": "Game started successfully"}), 200


@api_router.route('/api/get_player_view', methods=['POST'])
def get_player_view():
    """
    Get the game state for the given configuration.
    config format:
    {
        "unique_id": str
    }
    return:
    {
        "x": tile.x,
        "y": tile.y,
        "state": tile.state.value,
        "owner_id": player's unique id,
        "owner_color": player's color,
        "troops": tile.troops
    }
    """
    config = request.get_json()
    if not config:
        return jsonify({"error": "Invalid configuration"}), 400
    if not check_config(config, ['unique_id']):
        return jsonify({"error": "Missing configuration key"}), 400
    if config['unique_id'] not in users:
        return jsonify({"error": "Unique ID not found"}), 400
    if users[config['unique_id']]['game_id'] is None:
        return jsonify({"error": "User not in a game"}), 400
    game_id = users[config['unique_id']]['game_id']
    if games[game_id] is None:
        return jsonify({"error": "Game not started"}), 400
    player_info = users[config['unique_id']]['player_info']
    game_engine = games[game_id]
    game_board = game_engine.game_board
    game_map = game_engine.get_view(player_info)
    
    ## Convert the game map(Tile) to JSON serializable format
    game_map_json = []
    for row in game_map:
        row_json = []
        for tile in row:
            if tile.owner_id is None:
                tile_owner_unique_id = None
                tile_owner_color = None
            else:
                tile_owner_unique_id = game_board.players[tile.owner_id].unique_id 
                tile_owner_color = game_board.players[tile.owner_id].color
            tile_json = {
                "x": tile.x,
                "y": tile.y,
                "state": tile.state.value,
                "owner_id": tile_owner_unique_id,
                "owner_color": tile_owner_color,
                "troops": tile.troops
            }
            row_json.append(tile_json)
        game_map_json.append(row_json)
    return jsonify(game_map_json), 200
    
@api_router.route('/api/move', methods=['POST'])
def add_premove():
    """
    Move the troops for the given configuration.
    config format:
    {
        "unique_id": str,
        "from_x": int,
        "from_y": int,
        "direction": str,
        "troop_num": int
    }
    """
    config = request.get_json()
    if not config:
        return jsonify({"error": "Invalid configuration"}), 400
    if not check_config(config, ['unique_id', 'from_x', 'from_y', 'direction']):
        return jsonify({"error": "Missing configuration key"}), 400
    if config['unique_id'] not in users:
        return jsonify({"error": "Unique ID not found"}), 400
    if users[config['unique_id']]['game_id'] is None:
        return jsonify({"error": "User not in a game"}), 400
    game_id = users[config['unique_id']]['game_id']
    if games[game_id] is None:
        return jsonify({"error": "Game not started"}), 400
    player_info = users[config['unique_id']]['player_info']
    game_engine = games[game_id]
    if player_info is None:
        return jsonify({"error": "Player not in game"}), 400
    
    move_direction = config['direction']
    if move_direction not in Direction.__members__:
        return jsonify({"error": "Invalid direction"}), 400
    move_direction = Direction[move_direction]
    # if config["from_x"].isdigit() == False or config.isdigit()  == False:
    #     return jsonify({"error": "from_x and from_y should be integers"}), 400
    from_x = int(config['from_x'])
    from_y = int(config['from_y'])
    troop_num = config.get('troop_num', None)
    game_engine.add_premove(player_info, from_x, from_y, move_direction, troop_num)
    return jsonify({"message": "Move added successfully"}), 200


@api_router.route('/api/get_players', methods=['POST'])
def get_players():
    """
    Get the player information for the given configuration.
    config format:
    {
        "game_id": str
    }
    returns: names of player(format:{
        "name":str,
        "unique_id":str
    })
    """
    config = request.get_json()
    if not config:
        return jsonify({"error": "Invalid configuration"}), 400
    if not check_config(config, ['game_id']):
        return jsonify({"error": "Missing configuration key"}), 400
    if config['game_id'] not in games:
        return jsonify({"error": "Game ID not found"}), 400
    game_id = config['game_id']
    players_list = []
    for _user_id,_user in users.items():
        if _user['game_id'] == game_id:
            players_list.append({
                "name": _user['name'],
                "unique_id": _user_id
                })
    return jsonify(players_list), 200


@api_router.route('/api/is_game_started', methods=['POST'])
def is_game_started():
    """
    Check if the game has started for the given configuration.
    config format:
    {
        "game_id": str
    }
    returns: True or False
    """
    config = request.get_json()
    if not config:
        return jsonify({"error": "Invalid configuration"}), 400
    if not check_config(config, ['game_id']):
        return jsonify({"error": "Missing configuration key"}), 400
    if config['game_id'] not in games:
        return jsonify({"error": "Game ID not found"}), 400
    game_id = config['game_id']
    if games[game_id] is None:
        return jsonify({"isstarted": False}), 200
    else:
        return jsonify({"isstarted": True}), 200


@api_router.route('/api/get_game_state', methods=['POST'])
def get_game_state():
    """
    Get the game state for the given configuration.
    config format:
    {
        "game_id": str,
        "unique_id": str
    }
    returns: 
    {
        "isruning": bool,
        "is_calling_player_still_playing": bool,
        "game_state": {
            "players": [
                {
                    "name": str,
                    "color": str,
                    "isplaying": bool,
                    "troops": int,
                    "lands_num": int
                }
    """
    config = request.get_json()
    if not config:
        return jsonify({"error": "Invalid configuration"}), 400
    if not check_config(config, ['game_id', 'unique_id']):
        return jsonify({"error": "Missing configuration key"}), 400
    if config['game_id'] not in games:
        return jsonify({"error": "Game ID not found"}), 400
    if config['unique_id'] not in users:
        return jsonify({"error": "Unique ID not found"}), 400
    game_id = config['game_id']
    unique_id = config['unique_id']
    if users[unique_id]['game_id'] != game_id:
        return jsonify({"error": "User not in the game"}), 400
    if games[game_id] is None:
        return jsonify({"error": "Game not started"}), 400
    game_engine = games[game_id]
    calling_player = users[unique_id]['player_info']
    leader_board = game_engine.get_leader_board()
    is_game_end = game_engine.is_game_end()
    game_state = {
        "isruning": not is_game_end,
        "is_calling_player_still_playing": calling_player.playing,
        "leader_board": leader_board
    }
    return jsonify(game_state), 200

@api_router.route('/api/full_map', methods=['POST'])
def get_full_map():
    """
    Get the full map for the given configuration.
    config format:
    {
        "game_id": str,
        "unique_id": str
    }
    returns: 
    {
        "x": tile.x,
        "y": tile.y,
        "state": tile.state.value,
        "owner_id": player's unique id,
        "owner_color": player's color,
        "troops": tile.troops
    }
    """
    config = request.get_json()
    if not config:
        return jsonify({"error": "Invalid configuration"}), 400
    if not check_config(config, ['game_id', 'unique_id']):
        return jsonify({"error": "Missing configuration key"}), 400
    if config['game_id'] not in games:
        return jsonify({"error": "Game ID not found"}), 400
    if config['unique_id'] not in users:
        return jsonify({"error": "Unique ID not found"}), 400
    game_id = config['game_id']
    unique_id = config['unique_id']
    if users[unique_id]['game_id'] != game_id:
        return jsonify({"error": "User not in the game"}), 400
    if games[game_id] is None:
        return jsonify({"error": "Game not started"}), 400
    if users[unique_id]['player_info'] is None:
        return jsonify({"error": "Player not in game"}), 400
    if users[unique_id]['player_info'].playing == True:
        return jsonify({"error": "Player is still playing"}), 400
    game_engine = games[game_id]
    game_board = game_engine.get_full_map()
    game_map_json = []
    for row in game_board:
        row_json = []
        for tile in row:
            if tile.owner_id is None:
                tile_owner_unique_id = None
                tile_owner_color = None
            else:
                tile_owner_unique_id = game_board.players[tile.owner_id].unique_id 
                tile_owner_color = game_board.players[tile.owner_id].color
            tile_json = {
                "x": tile.x,
                "y": tile.y,
                "state": tile.state.value,
                "owner_id": tile_owner_unique_id,
                "owner_color": tile_owner_color,
                "troops": tile.troops
            }
            row_json.append(tile_json)
        game_map_json.append(row_json)
    return jsonify(game_map_json), 200