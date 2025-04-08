import pygame
from game.board import GameBoard
from game.game_types import TileType
from game.player import Player_Info

TILE_SIZE = 32
MARGIN = 2
FPS = 30

# Color by owner ID
OWNER_COLORS = [
    (200, 0, 0),    # Player 0 - Red
    (0, 200, 0),    # Player 1 - Green
    (0, 0, 200),    # Player 2 - Blue
    (200, 200, 0),  # Player 3 - Yellow
]

def load_and_scale_image(path):
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))

class PygameClint:
    def __init__(self, game_board: GameBoard):
        self.game_board = game_board

def draw_board(screen, board: GameBoard, font: pygame.font.Font, icons: dict):
    for x in range(board.width):
        for y in range(board.height):
            tile = board.map[x][y]
            rect = pygame.Rect(
                x * (TILE_SIZE + MARGIN),
                y * (TILE_SIZE + MARGIN),
                TILE_SIZE,
                TILE_SIZE
            )

            # Draw owner color as background
            owner_color = OWNER_COLORS[tile.owner_id % len(OWNER_COLORS)] if tile.owner_id is not None else (150, 150, 150)
            pygame.draw.rect(screen, owner_color, rect)

            # Draw tile type icon
            if tile.state in icons:
                screen.blit(icons[tile.state], rect.topleft)

            # Draw troops
            if tile.troops > 0:
                text = font.render(str(tile.troops), True, (50, 50, 50))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

def main():
    pygame.init()

    # Game board setup
    width, height = 15, 15
    players = [Player_Info(f"tst_{i}", i) for i in range(2)]
    board = GameBoard(width, height, players)
    print(board.initialize_map())
    print(board)
    

    screen = pygame.display.set_mode((
        width * (TILE_SIZE + MARGIN),
        height * (TILE_SIZE + MARGIN)
    ))
    pygame.display.set_caption("Generals Map Viewer")

    font = pygame.font.SysFont(None, 20)
    clock = pygame.time.Clock()

    # Load icons
    icons = {
        TileType.CITY: load_and_scale_image("res/city.png"),
        TileType.GENERAL: load_and_scale_image("res/general.png"),
        TileType.MOUNTAIN: load_and_scale_image("res/mountain.png"),
    }

    running = True
    while running:
        screen.fill((20, 20, 20))  # Background color

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_board(screen, board, font, icons)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()