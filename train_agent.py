import copy
import statistics
import config
from game.game_logic import HipGameLogic
from ai.agent import DQNAgent
from collections import deque


def run_training_session(agent, num_episodes=None, load_model_from='', save_model_to=''):
    game = HipGameLogic(board_size_x=agent.BOARD_SIZE_X, board_size_y=agent.BOARD_SIZE_Y)

    if load_model_from:
        try:
            agent.model.load(load_model_from)
            print(f'Loaded a pre-trained model {load_model_from}.')
        except FileNotFoundError:
            print(f'Could not load model {load_model_from}. Starting from scratch.')

    # For progess-tracking purposes.
    losers = deque(maxlen=config.ROLLING_AVG_WINDOW)
    game_length = deque(maxlen=config.ROLLING_AVG_WINDOW)

    while True:
        # A training cycle: 
        # get state -> get action -> perform action -> memorize the outcome -> train on a batch
        state = game.get_state()
        state_rep = state.get_state_rep()
        action = agent.select_action(state_rep)        
        if action == None:
            raise Exception(f'No valid action found for player {state.current_player}.')
        else:
            x, y = action
            action_rep = y * agent.BOARD_SIZE_X + x
            game.make_move(game.current_player, (x, y))
            next_state_rep = game.get_state().get_state_rep()
            done = game.player_lost != None 
        
        reward = agent.reward_function(state, game.get_state(), action)
        agent.memory.append((state_rep, action_rep, reward, next_state_rep, done))

        agent.train()

        if done:
            agent.games_played += 1            
            agent.epsilon = max(agent.epsilon_end, 
                                agent.epsilon_start - (agent.games_played / agent.epsilon_decay_games) * (agent.epsilon_start - agent.epsilon_end))

            losers.append(game.player_lost)
            game_length.append(game.moves_count)

            if not agent.games_played % config.ROLLING_AVG_WINDOW:
                print (f'Games played: {agent.games_played}',
                       f'epsilon: {agent.epsilon:.2f}',
                       f'P1 losing ratio: {losers.count(1) / len(losers):.2f}',
                       f'P2 losing ratio: {losers.count(2) / len(losers):.2f}',
                       f'Mean game length: {statistics.mean(game_length):.2f}')
                
            if not agent.games_played % config.SAVE_EVERY and save_model_to:
                agent.model.save(save_model_to)
            
            if num_episodes and agent.games_played >= num_episodes:
                break
            game.reset_game()

    print (f'Training finished after {agent.games_played} episodes.')

def reward_usual(cur_state, next_state, action):
    if action == None:
        return -20 # Penalty for not coming up with an action (should not happen normally).
    if next_state.player_lost == cur_state.current_player:
        return -5 # A loss.
    elif next_state.player_lost == 0:
        return 20 # A draw (maximally dense configuration).
    return 2 # Encourage continuation.


# A throwaway board to use in the cooperative reward calculations.
class TempBoard: 
    def __init__(self, board_size_x, board_size_y):
        self.board = None
        self.BOARD_SIZE_X = board_size_x
        self.BOARD_SIZE_Y = board_size_y

temp_board = TempBoard(config.BOARD_SIZE_X, config.BOARD_SIZE_Y)

def reward_cooperative(cur_state, next_state, action):
    if action is None:
        return -10 # Penalty for not coming up with an action (should not happen normally).
        
    if next_state.player_lost == 0:
        return 50 # A draw.
    if next_state.player_lost == cur_state.current_player:
        return -50 # A large penalty for a loss.
    
    x, y = action    
    temp_board.board = copy.deepcopy(next_state.board)    
    temp_board.board[y][x] = next_state.current_player     
    if HipGameLogic.find_square(temp_board, next_state.current_player):
        return 4 # Reward for covering cells unfavorable for the other player. 
    
    return 3 # Encourage continuation.


# agent = DQNAgent(config, reward_function=reward_usual, play_mode=False)

# run_training_session(agent, num_episodes=80000, save_model_to='models/usual_7_by_7.pth')

# run_training_session(agent, save_model_to='models/usual_7_by_7.pth')

agent = DQNAgent(config, reward_function=reward_usual, play_mode=False)

run_training_session(agent, num_episodes=50_000, save_model_to='models/usual_6_by_6.pth')
