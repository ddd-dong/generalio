# Generalio
![playing_img](readme_img\playing_img.png)

A small python project for personal use.

## Game rules

The game is a turn-based strategy game where players control armies and try to conquer the map. The game is played on a grid-based map, where each cell can be occupied by a player or be empty. Players can move their armies, attack other players, and capture territories.

### Map and Tiles:

The game is played on a grid-based map consisting of various tile types:​

- General Tile: Each player has one; losing it results in defeat.

- City Tiles: Neutral at the start; capturing them boosts army production.

- Empty Land Tiles: Neutral territory that can be captured to expand control.

- Mountain Tiles: Impassable barriers that block movement.

- Fog of War: Areas not visible to the player, hiding enemy movements and territories.

### Turns and Rounds:

The game progresses in turns, with specific actions occurring at set intervals:​

- Turn: A single opportunity for players to issue movement commands.

- Round: Comprises 25 turns; at the end of each round, additional armies are generated based on controlled land and cities.

### Army Generation:

- Per Turn:

Generals produce 1 army unit each turn.

Each controlled city produces 1 army unit each turn.

- Per Round:

At the end of every 25 turns (one round), each owned land tile contributes 1 additional army unit.

### Movement and Combat:

- Movement:

Armies can move to adjacent tiles (up, down, left, right) per turn.

Moving armies into neutral or enemy tiles initiates combat.

- Combat:

If the attacking army's size exceeds the defending army's size by at least one unit, the tile is captured, and the attacking army loses units equal to the defending army's size.

Capturing an enemy's general tile results in their defeat.

- Victory Conditions:

Capture all enemy generals to win the game.

## Structure

```txt
├── README.md
├── game # main logic of the game
│   ├── __init__.py
│   ├── board.py
│   ├── engine.py
│   ├── game_types.py
│   └── player.py
├── map_files # save and load generated maps
│   └── test_map.pkl
├── pygame_cli # pygame cli interface(not finished)
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-311.pyc
│   │   └── main.cpython-311.pyc
│   └── main.py
├── res # resources for the game(not used yet)
│   ├── city.png
│   ├── general.png
│   └── mountain.png
├── run.py # to run flask server of the game
├── server # flask server for the game
│   ├── __init__.py
│   ├── api.py
│   ├── app.py
│   ├── templates
│   │   ├── game.html
│   │   ├── home.html
│   │   └── waiting_room.html
│   └── utils.py # utility functions and classes(check config)
└── utils # utility functions and classes
    ├── __init__.py
    └── color.py
```

## API
![image](readme_img\generousio_server.drawio.png)
### POST `/api/create_user`
Create a new user.
**Request:**  
```json
{ "name": "player_name" }
```
**Response:**  
```json
{ "unique_id": "..." }
```

---

### POST `/api/new_game`
Create a new game.
**Request:**  
```json
{ "host_unique_id": "..." }
```
**Response:**  
```json
{ "game_id": "..." }
```

---

### POST `/api/join_game`
Join an existing game.
**Request:**  
```json
{ "game_id": "...", "unique_id": "..." }
```
**Response:**  
```json
{ "message": "Joined game successfully" }
```

---

### POST `/api/start_game`
Start a game with configuration.
**Request:**  
```json
{
  "hoster_unique_id": "...",
  "game_id": "...",
  "game_config": {
    "width": 10,
    "height": 10,
    "players": [
      { "name": "...", "unique_id": "..." }
    ],
    "optional": {
      "cities_fairness": 0.5,
      "cities_circles_radius_ratio": 0.3,
      "city_num": 5,
      "mountain_density": 0.2,
      "minimal_general_distance": 3
    }
  }
}
```
**Response:**  
```json
{ "isstart": true, "message": "Game started successfully" }
```

---

### POST `/api/get_player_view`
Get the visible map for a player.
**Request:**  
```json
{ "unique_id": "..." }
```
**Response:**  
Returns a 2D array of tiles, each tile:
```json
{
  "x": 0,
  "y": 0,
  "state": "...",
  "owner_id": "...",
  "owner_color": "...",
  "troops": 0
}
```

---

### POST `/api/move`
Add a move for a player.
**Request:**  
```json
{
  "unique_id": "...",
  "from_x": 0,
  "from_y": 0,
  "direction": "UP",
  "troop_num": 5
}
```
**Response:**  
```json
{ "message": "Move added successfully" }
```

---

### POST `/api/get_players`
Get all players in a game.
**Request:**  
```json
{ "game_id": "..." }
```
**Response:**  
List of players:
```json
[
  { "name": "...", "unique_id": "..." }
]
```

---

### POST `/api/is_game_started`
Check if a game has started.
**Request:**  
```json
{ "game_id": "..." }
```
**Response:**  
```json
{ "isstarted": true }
```

---

### POST `/api/get_game_state`
Get the current game state and leaderboard.
**Request:**  
```json
{ "game_id": "...", "unique_id": "..." }
```
**Response:**  
```json
{
  "isruning": true,
  "is_calling_player_still_playing": true,
  "leader_board": [
    {
      "name": "...",
      "color": "...",
      "isplaying": true,
      "troops": 0,
      "lands_num": 0
    }
  ]
}
```

---

### POST `/api/full_map`
Get the full map (for eliminated players).
**Request:**  
```json
{ "game_id": "...", "unique_id": "..." }
```
**Response:**  
2D array of tiles (same format as `/api/get_player_view`).

---
