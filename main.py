import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from game.game_logic import HipGameLogic
from game_graphics.rendering import HipGameGraphics
from game.player import HumanPlayer, RandomAIPlayer, AIPlayer
from collections import defaultdict

def run_single_game(screen, players):
    game = HipGameLogic(board_size_x=config.BOARD_SIZE_X, board_size_y=config.BOARD_SIZE_Y)
    game_graphics = HipGameGraphics(screen, players)
    game_graphics.draw_board(game.get_state())

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked_element, click_info = game_graphics.get_clicked_element(event.pos)
                if clicked_element == 'new_game_button':
                    game.reset_game()
                    game_graphics.draw_board(game.get_state())
                elif clicked_element == 'cell' and game.player_lost == None \
                    and players[game.current_player].is_human:
                        move = players[game.current_player].get_move(game.get_state(), click_info)
                        game.make_move(game.current_player, move)
                        game_graphics.draw_board(game.get_state())

        if game.player_lost == None and not players[game.current_player].is_human:
            # AI: given a board state, get a move from the bot.
            move = players[game.current_player].get_move(game.get_state())
            if move and game.make_move(game.current_player, move):
                game_graphics.draw_board(game.get_state())    
            else:
                raise Exception('AI could not make a valid move.')
            
        pygame.display.flip()
    
    return game.player_lost


def run_match(screen, players, num_rounds):
    lost_count = defaultdict(int)
    print(f'Starting a match of {num_rounds}.')

    for r_ in range(num_rounds):
        res = run_single_game(screen, players)
        lost_count[res] += 1
    
    print ('Loss counts:')
    for player_id, player in players.items():
        print (f'{player.player_name}: {lost_count[player_id]}')

if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption(config.GAME_TITLE)
    clock = pygame.time.Clock()

    players = {1: HumanPlayer('Player 1'), 2: HumanPlayer('Player 2')}
    run_single_game(screen, players)

    # players = {1: HumanPlayer('Player 1'), 2: AIPlayer('AI', 'models/usual_6_by_6.pth')}
    # run_match(screen, players, 5)

    pygame.quit()
    sys.exit()