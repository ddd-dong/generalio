from game_types import Tile, TileType
from typing import List

PLAYER_COLOR = {
    "red": "#FF0000",
    "blue": "#0000FF",
    "green": "#00FF00",
    "yellow": "#FFFF00",
    "purple": "#800080",
    "orange": "#FFA500",
    "pink": "#FFC0CB",
    "cyan": "#00FFFF",
    "brown": "#A52A2A"}

class Player:
    """
    need:
        - name: str
        - player_id: int(start from 0)
        - general position: Tile
        - total troops: int
        - total lands: int
        - total cities: int
        - color: str (optional)
    """
    def __init__(self, name: str, player_id: int):
        self.name = name
        self.id = player_id
        self.color = None
        self.general = None
        self.troops = 0
        self.cities = []
        self.cities_num = 0
        self.lands_num = 0
        self.lands = []
        self.playing = True
    
    def __repr__(self):
        output= f"Player {self.id} ({self.name})\n"
        output += f"Color: {self.color}\n"
        output += f"General: {self.general}\n"
        output += f"Troops: {self.troops} Cities number: {self.cities_num}\n"
        output += f"Cities: {self.cities}\n"
        return output
    
    def add_tile(self, tile: Tile)->None:
        """
        add tile to the player
        :param tile: Tile object
        """
        if tile.state == TileType.CITY:
            self.cities.append(tile)
            self.cities_num += 1
        if tile.state == TileType.GENERAL:
            raise Exception(f"General tile should be transferred to citiy before adding:{tile}")
        if tile.state == TileType.MOUNTAIN:
            raise Exception(f"Mountain tile can't be added:{tile}")
        self.lands += 1
        self.lands.append(tile)
    
    def update_numbers(self,map: List[List[Tile]]):
        """
        update the number of cities, lands, and troops
        :param map: map of the game from GameBoard
        """
        count_lands = 0
        count_troops = 0
        count_cities = 0
        for x in range(len(map)):
            for y in range(len(map[0])):
                tile = map[x][y]
                if tile.owner_id == self.id:
                    count_lands += 1
                    count_troops += tile.troops
                    if tile.state == TileType.CITY:
                        count_cities += 1
                        if tile not in self.cities:
                            print(f"------\n---\nWarning:City {tile} not in player.cities\n---\n------")
                            self.cities.append(tile)
        self.lands_num = count_lands
        self.troops = count_troops
        self.cities_num = count_cities

    def defeated(self):
        """called when player is defeated"""
        self.general = None
        self.troops = 0
        self.cities = []
        self.lands = []
        self.cities_num = 0
        self.lands_num = 0
        self.playing = False

        

        