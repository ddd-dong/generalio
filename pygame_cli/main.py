import pygame
from game.board import GameBoard
from game.game_types import TileType
from game.player import Player

TILE_SIZE = 32
MARGIN = 2
FPS = 30

COLOR_MAP = {
    TileType.EMPTY: (200, 200, 200),
    TileType.MOUNTAIN: (80, 80, 80),
    TileType.CITY: (0, 120, 255),
    TileType.GENERAL: (255, 100, 100),
}

class PygameClint:
    def __init__(self, game_board: GameBoard):
        self.game_board = game_board

def draw_board(screen, board: GameBoard, font: pygame.font.Font):
    for x in range(board.width):
        for y in range(board.height):
            tile = board.map[x][y]
            color = COLOR_MAP.get(tile.state, (255, 255, 255))
            rect = pygame.Rect(
                x * (TILE_SIZE + MARGIN),
                y * (TILE_SIZE + MARGIN),
                TILE_SIZE,
                TILE_SIZE
            )
            pygame.draw.rect(screen, color, rect)

            if tile.troops > 0:
                text = font.render(str(tile.troops), True, (255, 255, 255))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

def main():
    pygame.init()
    
    # Create and generate the map
    width, height = 15,15 # You can change this size
    players_num = 2
    players = []
    for i in range(players_num):
        players.append(Player(f"tst_{i}",i))
    board = GameBoard(width, height,players)
    print(board.initialize_map())
    print(board)

    screen = pygame.display.set_mode((
        width * (TILE_SIZE + MARGIN),
        height * (TILE_SIZE + MARGIN)
    ))
    pygame.display.set_caption("Generals Map Viewer")
    
    font = pygame.font.SysFont(None, 20)
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill((30, 30, 30))  # Background color

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_board(screen, board,font)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()