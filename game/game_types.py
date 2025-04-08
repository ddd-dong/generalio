import enum
from typing import List, Tuple, Dict, Optional, Set

class TileType(enum.Enum):
    EMPTY = "."
    MOUNTAIN = "#"
    CITY = "C"
    GENERAL = "G"
    UNKNOWN_OBSTACLE = "X" #mountain or city
    UNKNOWN_EMPTY = "?"  

class Direction(enum.Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    

class Tile:
    def __init__(self, x: int, y: int, state: TileType, owner_id: Optional[int] = None, troops: Optional[int] = 0):
        self.x = x
        self.y = y
        self.state = state
        self.owner_id = owner_id
        self.troops = troops
        assert self.troops >= 0, "Troops cannot be negative"
        assert isinstance(self.state, TileType), "State must be a TileType"
    
    def __repr__(self):
        return f"Tile(({self.x},{self.y}), {self.state}, owner={self.owner_id}, troops={self.troops})"

    def __eq__(self, other)->bool:
        assert isinstance(other, Tile), "Comparing Tile with non-Tile object"
        if self.x != other.x or self.y != other.y:
            return False
        if self.state != other.state or self.owner_id != other.owner_id or self.troops != other.troops:
            raise Exception(f"Tiles in same position are not equal: {self} != {other}")
        return True
    
    def __hash__(self):
        return hash((self.x, self.y, self.state, self.owner_id, self.troops))
        
        

