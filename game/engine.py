from game.board import GameBoard
from game.player import Player_Info
from game.game_types import TileType,Tile,Direction

from typing import List, Tuple, Dict, Any, TypeVar, Union


class GameEngine:
    def __init__(self,game_board: GameBoard):
        """
        Initializes the game engine with a game board.
        :param game_board: The game board to be used in the engine(*should be initialed first).
        """
        self.game_board = game_board
        self.players = game_board.players
        self.pre_moves_queue = [[] for _ in range(len(self.players))]
        self.game_board.check_board_vaildity()
        for i in range(len(self.players)):
            if self.players[i].id != i: 
                raise Exception(f"Player id should be same as the index of players list:{self.players[i]}")

    def add_premove(self, mover:Player_Info, from_x:int, from_y:int,direction:Direction, troop_num:int=None):
        if from_x < 0 or from_x >= self.game_board.width or from_y < 0 or from_y >= self.game_board.height:
            raise Exception(f"from_x:{from_x}, from_y:{from_y} is out of range")
        if troop_num is None: #move all troops
            self.pre_moves_queue[mover.id].append((mover,self.game_board.map[from_x][from_y],direction,None))
            return
        if troop_num <= 0:
            raise Exception(f"troop_num should be positive: {troop_num}")
        self.pre_moves_queue[mover.id].append((mover,self.game_board.map[from_x][from_y],direction,troop_num))

    def process_turn(self):
        move_this_turn = []
        for i in range(len(self.players)):
            if len(self.pre_moves_queue[i]) > 0:
                if self.pre_moves_queue[i][0][3] is None:
                    move_tmp = list(self.pre_moves_queue[i].pop(0))
                    move_tmp[3] = self.game_board.map[move_tmp[1].x][move_tmp[1].y].troops -1
                    move_this_turn.append(tuple(move_tmp))
                else:
                    move_this_turn.append(self.pre_moves_queue[i].pop(0))
            else:
                move_this_turn.append(())
        if len(move_this_turn) != self.game_board.player_num:
            raise Exception(f"Number of moves this turn is not equal to number of players: {len(move_this_turn)} != {self.game_board.player_num}")
        
        is_move_success = self.game_board.next_turn(move_this_turn)
        if len(is_move_success) != self.game_board.player_num:
            raise Exception(f"Number of moves success is not equal to number of players: {len(is_move_success)} != {self.game_board.player_num}")
        
        for i in range(self.game_board.player_num):
            if is_move_success[i] == False:
                self.pre_moves_queue[i].clear()
        
    def get_mask(self,player_info:Player_Info)->List[List[bool]]:
        """
        get the mask of the map for the player
        :param player_info: Player_Info object
        :return: mask of the map for the player(True for the tiles that can be sawn)
        """
        mask = [[False for _ in range(self.game_board.height)] for __ in range(self.game_board.width)]
        search_directions = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]
        for x in range(self.game_board.width):
            for y in range(self.game_board.height):
                if self.game_board.map[x][y].owner_id == player_info.id:
                    mask[x][y] = True
                    for dx,dy in search_directions:
                        if x+dx >= 0 and x+dx < self.game_board.width and y+dy >= 0 and y+dy < self.game_board.height:
                            mask[x+dx][y+dy] = True
        return mask
    
    def get_view(self,player_info:Player_Info)->List[List[Tile]]:
        """
        get the view of the map for the player
        :param player_info: Player_Info object
        :return: view of the map for the player
        """
        mask = self.get_mask(player_info)
        view = [[None for _ in range(self.game_board.height)] for __ in range(self.game_board.width)]
        for x in range(self.game_board.width):
            for y in range(self.game_board.height):
                if mask[x][y] == True:
                    view[x][y] = self.game_board.map[x][y]
                elif self.game_board.map[x][y].state == TileType.MOUNTAIN or\
                        self.game_board.map[x][y].state == TileType.CITY:
                    view[x][y] = Tile(x,y,TileType.UNKNOWN_OBSTACLE)
                else:
                    view[x][y] = Tile(x,y,TileType.UNKNOWN_EMPTY)
        return view
    
