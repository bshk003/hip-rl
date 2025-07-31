import collections
import config
from game.game_logic import HipGameLogic, HipGameState
import random, time
import torch
import numpy as np
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from ai.model import Linear_QNetwork, QTrainer

MAX_MEMORY = 100000
BATCH_SIZE = 64
LR = 0.001
SAVE_EVERY = 50 

# Rewards/penalties
REWARD_FOR_MOVE = 1
REWARD_FOR_LOSS = -5
REWARD_FOR_DRAW = 5
REWARD_FOR_NO_VALID_ACTION = -1

# REWARD_FOR_MOVE = 5
# REWARD_FOR_LOSS = -10
# REWARD_FOR_DRAW = 20
# REWARD_FOR_NO_VALID_ACTION = -1

TARGET_UPDATE_FREQUENCY = 300
ROLLING_AVG_WINDOW = 1000
class DQNAgent:
    def __init__(self, epsilon=1.0, model_filename=''):
        self.games_played = 0

        # The exploration parameter.
        self.epsilon_start = self.epsilon = epsilon
        self.epsilon_end = 0.01
        self.epsilon_decay_games = 5000

        # The discount factor. See Bellman's equation in ai.model.py.
        self.gamma = 0.9

        self.memory = collections.deque(maxlen=MAX_MEMORY)
        self.BOARD_SIZE_X = config.BOARD_SIZE_X
        self.BOARD_SIZE_Y = config.BOARD_SIZE_Y
        
        self.model = Linear_QNetwork(input_size=self.BOARD_SIZE_X*self.BOARD_SIZE_Y + 2, 
                                     hidden_size=512,
                                     output_size=self.BOARD_SIZE_X*self.BOARD_SIZE_Y)
        if model_filename:
            try:
                self.model.load(model_filename)
                print(f'Loaded a pre-trained model {model_filename}.')
            except FileNotFoundError:
                print(f'Could not load model {model_filename}. Starting a new training session.')
            return
        
        self.model_filename = model_filename
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.training_steps_count = 0

    def get_valid_actions(self, state_rep):
        # state_rep is a flattened board state with the current player ID + game over flag appended.
        return np.where(state_rep[:-2] == 0)[0] if state_rep[-1] == 0 else []

    def select_action(self, state_rep):
        valid_indices = self.get_valid_actions(state_rep)
        if valid_indices.size == 0:
            return None 
        
        if random.random() < self.epsilon:
            index = random.choice(valid_indices)
            y, x = divmod(index, self.BOARD_SIZE_X)
            return (x, y)
        else:
            state_tensor = torch.tensor(np.array(state_rep), dtype=torch.float32).unsqueeze(0)
            with torch.no_grad():
                q_values = self.model(state_tensor).squeeze()
            q_values_flat = q_values.flatten()
            # Argmaxing Q-values only over actions with valid indices.
            best_index = max(valid_indices, key=lambda i: q_values_flat[i])
            best_y, best_x = divmod(best_index, self.BOARD_SIZE_X)

            return (best_x, best_y)

    def train(self, batch_size=BATCH_SIZE):
        if len(self.memory) < batch_size:
            return None 
        
        batch = random.sample(self.memory, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.tensor(np.array(states), dtype=torch.float32)
        next_states = torch.tensor(np.array(next_states), dtype=torch.float32)
        rewards = torch.tensor(rewards, dtype=torch.float32)
        dones = torch.tensor(dones, dtype=torch.bool)

        loss = self.trainer.train_step(states, actions, rewards, next_states, dones)
        self.training_steps_count += 1

        if not self.training_steps_count % TARGET_UPDATE_FREQUENCY:
            self.trainer.update_target_model()
        
        return loss


def training_loop():
    agent = DQNAgent()
    game = HipGameLogic(board_size_x=agent.BOARD_SIZE_X, board_size_y=agent.BOARD_SIZE_Y)

    total_reward = 0
    losers = collections.deque(maxlen=ROLLING_AVG_WINDOW)
    game_length = collections.deque(maxlen=ROLLING_AVG_WINDOW)

    while True:
        # A training cycle: get state -> get action -> perform action -> memorize the outcome
        state_rep = game.get_state().get_state_rep()
        action = agent.select_action(state_rep)
        if action == None:
            print(f'Game {agent.games_played}: No valid action found.')
            done = True
            reward = REWARD_FOR_NO_VALID_ACTION # Penalize for no valid action.
            next_state_rep = state_rep
        else:
            x, y = action
            game.make_move(game.current_player, (x, y))
            next_state_rep = game.get_state().get_state_rep()
            done = game.player_lost != None
            # Reward for making a valid move. Penalize for losing. 
            reward = REWARD_FOR_LOSS if done and game.player_lost else REWARD_FOR_MOVE

        agent.memory.append((state_rep, action, reward, next_state_rep, done))
        total_reward += reward 

        if done:
            agent.games_played += 1
            
            agent.epsilon = max(agent.epsilon_end, 
                                agent.epsilon_start - (agent.games_played / agent.epsilon_decay_games) * (agent.epsilon_start - agent.epsilon_end))

            losers.append(game.player_lost)
            game_length.append(game.moves_count)

            if not agent.games_played % ROLLING_AVG_WINDOW:
                print (f'Games played: {agent.games_played}',
                       f'epsilon: {agent.epsilon:.2f}',
                       f'P1 losing ratio: {losers.count(1) / len(losers):.2f}',
                       f'P2 losing ratio: {losers.count(2) / len(losers):.2f}',
                       f'Mean game length: {np.mean(game_length):.2f}')
            if not agent.games_played % SAVE_EVERY:
                agent.model.save()

            total_reward = 0
            game.reset_game()

    
if __name__ == '__main__':
    training_loop()
