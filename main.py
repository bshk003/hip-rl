import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from game.game_logic import HipGameLogic
from game_graphics.rendering import HipGameGraphics
from game.player import HumanPlayer, RandomAIPlayer, AIPlayer

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption(config.GAME_TITLE)
    clock = pygame.time.Clock()

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
            # AI: given a board state, get the AI's move.
            move = players[game.current_player].get_move(game.get_state())
            if move and game.make_move(game.current_player, move):
                game_graphics.draw_board(game.get_state())    
            else:
                raise Exception('AI could not make a valid move.')    

    pygame.quit()
    sys.exit()

players = {2: HumanPlayer('Player 1'), 
           1: AIPlayer('AI', model_filename='models/model_66_longplay.pth')} 

if __name__ == "__main__":
    run_game()