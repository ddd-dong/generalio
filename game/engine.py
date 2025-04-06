from game.board import GameBoard
from game.player import Player
from game.game_types import TileType,Tile

from typing import List, Tuple, Dict, Any, TypeVar, Union


class GameEngine:
    def __init__(self,game_board: GameBoard):
        """
        Initializes the game engine with a game board.
        :param game_board: The game board to be used in the engine(*should be initialed first).
        """
        self.game_board = game_board
        self.players = game_board.players
        
        self.game_board.check_board_vaildity()

    
