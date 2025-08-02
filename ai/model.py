import torch
import numpy as np
import torch.nn as nn
import torch.optim as optim
import os

class Linear_QNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        # Two layers seem to work OK-ish.
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        x = torch.relu(self.linear1(x))
        x = self.linear2(x)
        return x
    
    def save(self, model_filename):
        # if not os.path.exists('models'):
        #     os.makedirs('models')
        try:
            torch.save(self.state_dict(), model_filename)
        except Exception as e:
            print(f'Could not save the model to {model_filename} due to {type(e).__name__}.')
            raise e

    def load(self, model_filename):
        try:
            self.load_state_dict(torch.load(model_filename, weights_only=True))
        except Exception as e:
            print(f'Could not load a model from {model_filename} due to {type(e).__name__}.')
            raise e
        
class QTrainer():
    def __init__(self, model, lr=0.001, gamma=0.9):
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=lr)
        self.criterion = nn.MSELoss() 

        self.target_model = Linear_QNetwork(model.linear1.in_features,
                                            model.linear1.out_features,
                                            model.linear2.out_features)

        self.target_model.load_state_dict(self.model.state_dict())
        self.target_model.eval()

    def train_step(self, states, actions, rewards, next_states, dones):
        # states - (BATCH_SIZE, input_size), where input_size = BOARD_SIZE_X*BOARD_SIZE_Y+2
        # actions - a list of flattened (x,y) coordinates, length BATCH_SIZE
        # rewards - (BATCH_SIZE,)
        # next_states - (BATCH_SIZE, input_size)
        # dones - (BATCH_SIZE,) bool

        self.model.train() # Important: unlike target_model, model is in the train mode.

        pred_q_values = self.model(states) # Shape: (BATCH_SIZE, output_size)        
        pred_q_values_for_action = pred_q_values[range(len(actions)), actions]

        with torch.no_grad(): 
            next_q_values_all_actions = self.target_model(next_states) # Shape: (BATCH_SIZE, output_size)
          
            # For each next_state, maximize the Q-value over all possible actions.
            max_next_q_values, _ = next_q_values_all_actions.max(dim=1) # Shape: (BATCH_SIZE,)
            # Bellman's equation: relate target Q-values to the predicted ones.
            targets = rewards + self.gamma * max_next_q_values * (~dones)
        
        loss = self.criterion(pred_q_values_for_action, targets)

        self.optimizer.zero_grad() 
        loss.backward()             
        self.optimizer.step()  

        return loss.item()     

    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())
        self.target_model.eval()