from game_types import Tile,TileType
import random
from typing import List, Tuple, Dict, Optional, Set,Any
from player import Player


GAME_DEFAULTS = {
    "CITIES_INITIAL_TROOPS_RANGE": (40, 51),
    "CITY_TROOPS_INCREASE": 1, #each turn
    "IS_RECORD_HISTORY": True,
    "HISTORY_RECORDING_INTERVAL": 1, #turn
    "HISTORY_RECORDING_MAX_SIZE": 50000, #turn
    "HISTORY_RECORDING_DIR": "/game_history",
    "TURN_PER_ROUND": 25, #turn
}


def manhattan_distance(p1:Tile, p2:Tile) -> int:
    """
    Calculate the Manhattan distance between two tiles.
    """
    return abs(p1.x - p2.x) + abs(p1.y - p2.y)


class GameBoard:
    def __init__(self,width: int, height: int, players:List[Player],cities_fairness:float=1.0,cities_circles_radius_ratio:float=0.5, 
                 city_num:int=0, mountain_density:float=0.2, minimal_general_distance:int = 15,game_defaults:Dict[str, Any]=GAME_DEFAULTS):
        """
        Initialize the game board with the given parameters.
        :param width: Width of the board
        :param height: Height of the board
        :param players: List of players
        :param city_num: Number of cities on the board
        :param cities_initial_troops: Initial troops in each city
        :param cities_fairness: Fairness of city distribution (0-1)
        :param cities_circles_radius_ratio: Ratio of citiy circle radius to minimal_general_distance(0-1)
        :param mountain_density: Probability of mountain be generated in a tile(0-1)
        :param minimal_general_distance: Minimal distance between generals
        """
        assert cities_fairness >= 0 and cities_fairness <= 1, "cities_fairness must be between 0 and 1"
        assert city_num >= 0, "city_num cannot be negative"
        assert mountain_density >= 0 and mountain_density <= 1, "mountain_density must be between 0 and 1"
        assert minimal_general_distance >= 0, "minimal_general_distance cannot be negative"
        assert cities_circles_radius_ratio >= 0 and cities_circles_radius_ratio <= 1, "cities_circles_radius_ratio must be between 0 and 1"
        for _key, _value in GAME_DEFAULTS.items():
            if _key not in game_defaults:
                game_defaults[_key] = _value
                print(f"Warning: {_key} not in game_defaults, set to default value: {_value}")

        self.width = width
        self.height = height
        self.player_num = len(players)
        self.players = players
        self.city_num = city_num
        self.mountain_density = mountain_density
        self.cities_initial_troops_range = game_defaults["CITIES_INITIAL_TROOPS_RANGE"]
        self.minimal_general_distance = minimal_general_distance
        self.cities_fairness = cities_fairness
        self.cities_circles_radius_ratio = cities_circles_radius_ratio

        self.map = []
        self.generals = []
        self.cities = []
        self.mountains = []
        self.map = [[Tile(x, y, TileType.EMPTY) for y in range(self.height)] for x in range(self.width)]
        self.players_defeated = []

        self.move_queue = [[] for i in range(self.player_num)] # each player has a queue of moves to be executed in order
        self.turn = 0
        self.round = 0
        self.turn_per_round = game_defaults["TURN_PER_ROUND"]
        self.city_troops_increase = game_defaults["CITY_TROOPS_INCREASE"]

        self.is_record_history = game_defaults["IS_RECORD_HISTORY"]
        self.history_recording_interval = game_defaults["HISTORY_RECORDING_INTERVAL"]
        self.history_recording_max_size = game_defaults["HISTORY_RECORDING_MAX_SIZE"]
        self.history_recording_dir = game_defaults["HISTORY_RECORDING_DIR"]
        self.history = []
    
    def initialize_map(self,maximum_tries:int=3)-> Tuple[bool, str]:
        """
        reset the map to empty tiles
        set generals, cities and mountains to their respective positions follow the rules:
            1. generals must be at least minimal_general_distance away from each other
            2. every general should be able to reach each city and general
            3. generals, mountains and cities cannot be on the same tile 
            4. Cities's position should be fairly distributed.
        The process is as follows:
            1. Set generals(ensure distance)
            2. Set Cities(ensure connectivity,and fair distribution)
            3. Set mountains(ensure distance)
        """
        self.map = [[Tile(x, y, TileType.EMPTY) for y in range(self.height)] for x in range(self.width)]
        tries_count = 0
        error_msg = ""
        while tries_count < maximum_tries:
            try:
                self.map = []
                self.generals = []
                self.cities = []
                self.mountains = []
                self.map = [[Tile(x, y, TileType.EMPTY) for y in range(self.height)] for x in range(self.width)]
                self._set_generals()
            except Exception as e:
                return False,str(e)
            try:
                self._set_cities()
                self._set_mountains()
                if self.check_board_vaildity():
                    return True, "Map initialized successfully"
                
            except Exception as e:
                tries_count += 1
                print(f"Retrying... ({tries_count}/{maximum_tries})\n error: {e}")
                error_msg = str(e)
                if tries_count >= maximum_tries:
                    return False, f"Map initialization failed after maximum tries \n error: {error_msg}"
        raise Exception(f"Map initialization failed")
    
    

    def move(self, from_tile: Tile, to_tile: Tile, moved_troops:int) -> bool:
        """
        Move a troop from one tile to another.
        return True if the move is successful(mean the following pre-move need be procceded), False otherwise.
        """

        if manhattan_distance(from_tile, to_tile) > 1:
            return False
        if from_tile.troops <= 1:
            return False
        if to_tile.state == TileType.MOUNTAIN:
            return False
        if from_tile.state == TileType.MOUNTAIN:
            return False
        if from_tile.troops <= moved_troops:
            return False
        if moved_troops <= 0:
            return False
        if to_tile.owner_id == None and to_tile.troops == 0:
            from_tile.troops -= moved_troops
            to_tile.troops = moved_troops
            to_tile.owner_id = from_tile.owner_id
            return True
        if from_tile.owner_id != to_tile.owner_id:
            return self.combat(from_tile, to_tile, moved_troops)
        if from_tile.owner_id == to_tile.owner_id:
            to_tile.troops += (from_tile.troops - 1)
            from_tile.troops = 1
            return True
        else:
            raise Exception(f"Invalid move: I don't why this happened\nfrom_tile: {from_tile}, to_tile: {to_tile}")
        

    def combat(self, attacker: Tile, defender: Tile, attacker_troops:int) -> bool:
        """Should only be called through move()"""
        if defender.troops >= attacker.troops:
            defender.troops -= attacker_troops
            attacker.troops -= attacker_troops
            return False
        if defender.troops < attacker_troops:
            defender.owner_id = attacker.owner_id
            defender.troops =  attacker_troops - defender.troops
            attacker.troops -= attacker_troops
            if defender.state == TileType.GENERAL:
                self.defeat_player(self.players[defender.owner_id])
            self.players[attacker.owner_id].add_tile(defender)
            return True

    def check_end_game(self) -> bool:
        """called after each turn"""
        if len(self.players_defeated) == self.player_num - 1:
            return True
        return False

    def defeat_player(self, losser: Player, conqueror: Player):
        """
        Defeat a player, transfer their general to city, give all their lands to the conqueror
        """
        self.players_defeated.append(losser)
        # transfer general to city
        losser.general.state = TileType.CITY
        losser.general = None
        # the following process(add this city to conqueror's cities) will be done in combat()

        # transfer all lands to conqueror 
        for x in range(self.width):
            for y in range(self.height):
                tile = self.map[x][y]
                if tile.owner_id == losser.id:
                    tile.owner_id = conqueror.id
                    conqueror.add_tile(tile)
        conqueror.update_numbers(self.map)



    def __getitem__(self, pos: Tuple[int, int]) -> Tile:
        assert isinstance(pos, tuple), "pos must be a tuple"
        assert len(pos) == 2, "pos must be a tuple of length 2"
        return self.map[pos[0]][pos[1]]
    
    def __setitem__(self, pos: Tuple[int, int], value: Tile)-> None:
        assert isinstance(pos, tuple), "pos must be a tuple"
        assert len(pos) == 2, "pos must be a tuple of length 2"
        assert isinstance(value, Tile), "value must be a Tile"
        assert value.x == pos[0] and value.y == pos[1], "value must be a Tile with the same position as pos"
        self.map[pos[0]][pos[1]] = value


    def __repr__(self):
        """
        Print the map in a readable format.
        """
        output = f"GameBoard({self.width} X {self.height}, player: {self.player_num})\n"
        for y in range(self.height):
            for x in range(self.width):
                tile = self.map[x][y]
                output += tile.state.value
                output += " "
            output += "\n"
        return output

    def _set_generals(self):
        """
        Set generals to the map, ensuring that they are at least minimal_general_distance away from each other.
        """
        def _check_minimal_general_distance(candidates:Tile,solution):
            """
            Check if the generals are at least minimal_general_distance away from each other.
            """
            for tile in solution:
                if manhattan_distance(candidates,tile) < self.minimal_general_distance:
                    return False
            return True


        def _backtrack(solution,candidates):
            """
            Backtrack to find a solution for the generals.
            """
            if len(solution) == self.player_num:
                return solution

            random.shuffle(candidates)

            for i,candidate in enumerate(candidates):
                if _check_minimal_general_distance(candidate,solution):
                    new_solution = solution.copy()
                    new_solution.append(candidate)
                    new_candidates = candidates.copy()
                    new_candidates.pop(i)
                    result = _backtrack(new_solution,new_candidates)
                    if result is not None:
                        return result
            return None
        all_tiles = [self.map[x][y] for x in range(self.width) for y in range(self.height)]
        self.generals = _backtrack([],all_tiles)
        if self.generals is None:
            raise Exception("No solution found for generals")
        for i,general in enumerate(self.generals):
            general_tile = Tile(general.x,general.y,TileType.GENERAL,i)
            self.generals[i] = general_tile
            self.map[general.x][general.y] = general_tile
            self.players[i].general = general_tile

    def _set_cities(self):
        """
        Must be called after generals are set.
        Set cities to the map, ensuring that they are at least fair for each player.
        (cities_num/player_num)*cities_fairness = cities number in each player's circle
        cities_num - cities number in each player's circle = cities number in random playes out of the circles
        """
        # draw a circle around each general, ensure each circles are not overlapping
        # mark tiles in the circles and out of the circles
        generals_circle = []
        isin_circles = [[False for y in range(self.height)] for x in range(self.width)]
        for general in self.generals:
            circle = []
            for x in range(self.width):
                for y in range(self.height):
                    tile = self.map[x][y]
                    if tile.state == TileType.GENERAL:
                        isin_circles[x][y] = True
                    elif manhattan_distance(tile, general) <= int(self.minimal_general_distance*self.cities_circles_radius_ratio):
                        circle.append(tile)
                        isin_circles[x][y] = True
            random.shuffle(circle)
            generals_circle.append(circle)
        cities_num_in_circle = int((self.city_num/self.player_num)*self.cities_fairness)
        cities_num_out_circle = self.city_num - cities_num_in_circle*self.player_num
        for p_id,circle in enumerate(generals_circle):
            for i in range(cities_num_in_circle):
                city = Tile(circle[i].x,circle[i].y,TileType.CITY,troops=random.randint(self.cities_initial_troops_range[0],self.cities_initial_troops_range[1]))
                self.map[city.x][city.y] = city
                self.cities.append(city)

        # set cities out of the circles
        cities_out_circle = [self.map[x][y] for x in range(self.width) for y in range(self.height) if isin_circles[x][y] == False]
        if len(cities_out_circle) < cities_num_out_circle:
            print(isin_circles)
            print(cities_out_circle)
            raise Exception(f"""Not enough cities out of the circles: {len(cities_out_circle)} < {cities_num_out_circle}
            cities_num: {self.city_num}, player_num: {self.player_num}, cities_fairness: {self.cities_fairness}, cities_circles_radius_ratio: {self.cities_circles_radius_ratio}
            isin_circles: {isin_circles}
            cities_out_circle: {cities_out_circle}
            cities_num_out_circle: {cities_num_out_circle}""")        
        random.shuffle(cities_out_circle)
        for i in range(cities_num_out_circle):
            city = Tile(cities_out_circle[i].x,cities_out_circle[i].y,TileType.CITY,troops=random.randint(self.cities_initial_troops_range[0],self.cities_initial_troops_range[1]))
            self.map[city.x][city.y] = city
            self.cities.append(city)
    
    def get_reachable_tiles(self, start: Tile) -> List[Tile]:
        """
        return all reachable tiles from start tile
        """
        visited = [[False for y in range(self.height)] for x in range(self.width)]
        reachable_tiles = []
        def _dfs(tile: Tile):
            if visited[tile.x][tile.y]:
                return
            visited[tile.x][tile.y] = True
            reachable_tiles.append(tile)
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                x = tile.x + dx
                y = tile.y + dy
                if x < 0 or x >= self.width or y < 0 or y >= self.height:
                    continue
                if self.map[x][y].state == TileType.MOUNTAIN:
                    continue
                _dfs(self.map[x][y])
        _dfs(start)
        return reachable_tiles
            
    def get_all_connected_tiles(self):
            visited = [[False for y in range(self.height)] for x in range(self.width)]
            isolated_tiles = []
            for x in range(self.width):
                for y in range(self.height):
                    if visited[x][y]:
                        continue
                    if self.map[x][y].state == TileType.MOUNTAIN:
                        continue
                    conntected_tiles = self.get_reachable_tiles(self.map[x][y])
                    for tile in conntected_tiles:
                        visited[tile.x][tile.y] = True
                    isolated_tiles.append(conntected_tiles)
            return isolated_tiles

    def _set_mountains(self):
        """
        Set mountains to the map, ensuring connectivity
        """
        # randomly set mountains to the map
        for x in range(self.width):
            for y in range(self.height):
                if self.map[x][y].state == TileType.GENERAL or self.map[x][y].state == TileType.CITY:
                    continue
                if random.random() < self.mountain_density:
                    tile = Tile(x, y, TileType.MOUNTAIN)
                    self.map[x][y] = tile
                    self.mountains.append(tile)

        # check if the map is connected
        isolated_tiles = self.get_all_connected_tiles()
        isolated_tiles_num = len(isolated_tiles)
        # delete some mountains to ensure connectivity
        for i in range(isolated_tiles_num-1):
            tiles_chunk_A = isolated_tiles[0]
            finia_chunk_b_indx = None
            min_distance = self.width + self.height+1
            min_tile_pair = [None, None]
            for j in range(len(isolated_tiles[1:])):
                tiles_chunk_B = isolated_tiles[j+1]
                for tile_A in tiles_chunk_A:
                    for tile_B in tiles_chunk_B:
                        distance = manhattan_distance(tile_A, tile_B)
                        if distance < min_distance:
                            min_distance = distance
                            min_tile_pair = [tile_A, tile_B]
                            finia_chunk_b_indx = j+1
            if min_tile_pair[0] is None or min_tile_pair[1] is None:
                raise Exception(f"""
                No solution found for mountains
                isolated_tiles: {isolated_tiles}
                min_tile_pair: {min_tile_pair}""")
            isolated_tiles[0].extend(isolated_tiles[finia_chunk_b_indx])
            isolated_tiles.pop(finia_chunk_b_indx)
            # delete the mountain between the two chunks
            tile_A = min_tile_pair[0]
            tile_B = min_tile_pair[1]
            from_x = tile_A.x
            from_y = tile_A.y
            to_x = tile_B.x
            to_y = tile_B.y
            while (from_x,from_y) != (to_x,to_y):
                possible_directions = []
                if from_x < to_x:
                    possible_directions.append((1,0))
                elif from_x > to_x:
                    possible_directions.append((-1,0))
                if from_y < to_y:
                    possible_directions.append((0,1))
                elif from_y > to_y:
                    possible_directions.append((0,-1))
                dx,dy = random.choice(possible_directions)
                from_x += dx
                from_y += dy
                if self.map[from_x][from_y].state == TileType.MOUNTAIN:
                    self.mountains.remove(self.map[from_x][from_y])
                    self.map[from_x][from_y] = Tile(from_x, from_y, TileType.EMPTY)
                    
        # check if the map is connected again
        isolated_tiles = self.get_all_connected_tiles()
        if len(isolated_tiles) > 1:
            raise Exception(f"Map is not connected after setting mountains: {isolated_tiles}")
        
        
    def check_board_vaildity(self) -> bool:
        """
        Check if the board is valid.
        0. Check width, height, city_num
        1. There are as many general as player_num, and generals are at least minimal_general_distance away from each other.
        2. Connecitivity: every tile can reach every other tile.
        """
        if len(self.players_defeated) != 0:
            raise Exception(f"check_board_vaildity() should be called before game starts")
        # check width, height, city_num
        if len(self.map) != self.width or len(self.map[0]) != self.height:
            raise Exception(f"Map size is not equal to width and height: {len(self.map)} X {len(self.map[0])} != {self.width} X {self.height}")
        count_cities = sum([1 for x in range(self.width) for y in range(self.height) if self.map[x][y].state == TileType.CITY])
        if self.city_num != len(self.cities) or self.city_num != count_cities:
            raise Exception(f"Number of cities is not equal to city_num: {len(self.cities)}(self.cities) != {self.city_num} or {count_cities}(cities in map) != {self.city_num}")
        if len(self.generals) != self.player_num:
            raise Exception(f"Number of generals is not equal to number of players: {len(self.generals)} != {self.player_num}")
        # check generals in the map if same as self.generals(number, onwer_id, ensure each player has a general)
        generals_in_map = [self.map[x][y] for x in range(self.width) for y in range(self.height) if self.map[x][y].state == TileType.GENERAL]
        if len(generals_in_map) != self.player_num:
            raise Exception(f"Number of generals in the map is not equal to number of players: {len(generals_in_map)} != {self.player_num}")
        for player in self.players:
            if player.general.state != TileType.GENERAL or player.general.owner_id != player.id:
                raise Exception(f"Player {player.name} does not have a general\nplyaer:{player} ")
        # check generals_in_map if same as self.generals
        if set(generals_in_map) != set(self.generals):
            raise Exception(f"Generals in the map is not equal to generals: {generals_in_map} != {self.generals}")
        # check generals distance
        for i in range(len(self.generals)):
            for j in range(i+1, len(self.generals)):
                if manhattan_distance(self.generals[i], self.generals[j]) < self.minimal_general_distance:
                    raise Exception(f"Generals are too close: {self.generals[i]} and {self.generals[j]}")
        # check connectivity
        isolated_tiles = self.get_all_connected_tiles()
        if len(isolated_tiles) > 1:
            raise Exception(f"Map is not connected: chunk_number:{len(isolated_tiles)}\n{isolated_tiles}")
        # check if every general can reach other generals
        connected_tiles = self.get_reachable_tiles(self.generals[0])
        for i in range(1, len(self.generals)):
            if self.generals[i] not in connected_tiles:
                raise Exception(f"General {self.generals[i]} cannot reach general {self.generals[0]}")
        return True

if __name__ == "__main__":
    # Test the GameBoard class
    
    players = []
    player_num = 3
    for i in range(player_num):
        players.append(Player(f"Player {i}", i))
    test = GameBoard(15, 15,  players,city_num=8)
    # print(test[0,1])
    # test[0,1] = Tile(0,1,TileType.CITY)
    print(test.initialize_map())
    print(test)
