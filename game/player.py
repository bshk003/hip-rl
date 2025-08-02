from abc import ABC, abstractmethod
import random
import config
from ai.agent import DQNAgent

# An abstract superclass for both human and AI players.
class Player(ABC):
    def __init__(self, player_name, is_human=False):
        self.is_human = is_human
        self.player_name = player_name

    @abstractmethod
    def get_move(self, game_state, click_info=None):
        pass

class HumanPlayer(Player):
    def __init__(self, player_name):
        super().__init__(player_name, is_human=True)

    def get_move(self, game_state, click_info):
        # For human players, the move is determined by mouse click.
        return click_info


class RandomAIPlayer(Player):
    def __init__(self, player_name):
        super().__init__(player_name, is_human=False)

    def get_move(self, game_state, click_info=None):
        # Randomly select a valid move.
        valid_moves = [(x, y) for y in range(config.BOARD_SIZE_Y)
                       for x in range(config.BOARD_SIZE_X)
                       if game_state.board[y][x] == 0]
        return random.choice(valid_moves) if valid_moves else None

class AIPlayer(Player):
    def __init__(self, player_name, model_filename):
        super().__init__(player_name, is_human=False)
        self.agent = DQNAgent(config, play_mode=True)
        try:
            self.agent.model.load(model_filename)
            print(f'Playing against AI. Loaded trained model {model_filename}.')
        except FileNotFoundError:
            print(f'No model {model_filename} found.')
            return

    def get_move(self, game_state, click_info=None):
        return self.agent.select_action(game_state.get_state_rep())