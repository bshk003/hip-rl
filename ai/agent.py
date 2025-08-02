import collections
import random
import torch
import numpy as np
import torch.nn as nn
import torch.optim as optim
from ai.model import Linear_QNetwork, QTrainer

class DQNAgent:
    def __init__(self, config, reward_function=None, play_mode=False):
        self.config = config
        self.reward_function = reward_function
        self.play_mode = play_mode # True for playing, False for training.

        # The exploration parameter.
        self.epsilon_start = self.epsilon = config.EPSILON_START
        self.epsilon_end = config.EPSILON_END
        self.epsilon_decay_games = config.EPSILON_DECAY

        # The discount factor. See Bellman's equation in ai.model.py.
        self.gamma = config.GAMMA

        self.memory = collections.deque(maxlen=config.MAX_MEMORY)
        self.batch_size = config.BATCH_SIZE

        self.BOARD_SIZE_X = config.BOARD_SIZE_X
        self.BOARD_SIZE_Y = config.BOARD_SIZE_Y    
        
        self.model = Linear_QNetwork(input_size=self.BOARD_SIZE_X*self.BOARD_SIZE_Y + 2, 
                                     hidden_size=256,
                                     output_size=self.BOARD_SIZE_X*self.BOARD_SIZE_Y)
        
        self.trainer = QTrainer(self.model, lr=config.LR, gamma=self.gamma)
        self.games_played = self.training_steps_count = 0


    def get_valid_actions(self, state_rep):
        # state_rep is a flattened board state with the current player ID + game over flag appended.
        # Return the indicies of the board cells with the zero values (the empty ones).
        return np.where(state_rep[:-2] == 0)[0] if state_rep[-1] == 0 else []

    def select_action(self, state_rep):
        valid_indices = self.get_valid_actions(state_rep)
        if valid_indices.size == 0:
            return None 
        
        # No randomness in the play mode.
        if not self.play_mode and random.random() < self.epsilon:
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

    def train(self):
        if len(self.memory) < self.batch_size:
            return None 
        
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.tensor(np.array(states), dtype=torch.float32)
        actions = torch.tensor(actions, dtype=torch.int32)
        next_states = torch.tensor(np.array(next_states), dtype=torch.float32)
        rewards = torch.tensor(rewards, dtype=torch.float32)
        dones = torch.tensor(dones, dtype=torch.bool)

        loss = self.trainer.train_step(states, actions, rewards, next_states, dones)
        self.training_steps_count += 1

        if not self.training_steps_count % self.config.TARGET_UPDATE_FREQUENCY:
            self.trainer.update_target_model()
        
        return loss