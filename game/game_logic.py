import numpy as np

class HipGameState:
    def __init__(self, board, current_player, player_lost, square_found):
        self.board = board
        self.current_player = current_player
        self.player_lost = player_lost
        self.square_found = square_found

    def get_state_rep(self):
        res = np.array(self.board).flatten()
        # Normalize player ID to -0.5 or 0.5 and append the game over flag.
        return np.append(res, [self.current_player - 1.5, float(self.player_lost != None)]) 
class HipGameLogic:
    def __init__(self, board_size_x, board_size_y):
        self.BOARD_SIZE_X = board_size_x
        self.BOARD_SIZE_Y = board_size_y
        self.current_player = 1 # Player 1 starts.
        self.board = [[0 for _ in range(board_size_x)] for _ in range(board_size_y)]
        self.player_lost = None
        self.square_found = None   
        self.moves_count = 0

    def make_move(self, player, action):
        x, y = action
        if not (0 <= x < self.BOARD_SIZE_X and 0 <= y < self.BOARD_SIZE_Y) or self.board[y][x]:
            return False  # The cell is already occupied or is out of bounds.

        self.moves_count += 1
        self.board[y][x] = player
        found = self.check_for_loser()
        if found:
            self.square_found = found
            self.player_lost = player
            return True
        elif self.check_for_draw():
            self.player_lost = 0
            return True
        else:
            self.current_player = 2 if player == 1 else 1
            return True

    def check_for_loser(self):
        # Check for a square made of the current player's pieces.
        for y1 in range(self.BOARD_SIZE_Y):
            for x1 in range(self.BOARD_SIZE_X):
                if self.board[y1][x1]:
                    cur = self.board[y1][x1]
                    for y2 in range(y1, self.BOARD_SIZE_Y):
                        for x2 in range(x1, self.BOARD_SIZE_X):
                            if y1 == y2 and x1 == x2:
                                continue
                            if self.board[y2][x2] == cur:
                                delta_y = y2 - y1
                                delta_x = x2 - x1
                                y3 = y2 + delta_x
                                x3 = x2 - delta_y
                                y4 = y1 + delta_x
                                x4 = x1 - delta_y
                                if (0 <= y3 < self.BOARD_SIZE_Y and 0 <= x3 < self.BOARD_SIZE_X
                                        and 0 <= y4 < self.BOARD_SIZE_Y and 0 <= x4 < self.BOARD_SIZE_X) \
                                        and (self.board[y3][x3] == self.board[y4][x4] == cur):
                                    self.square_found = ((x1, y1), (x2, y2), (x3, y3), (x4, y4))
                                    return self.square_found
        return None 
    
    def reset_game(self):
        self.board = [[0 for _ in range(self.BOARD_SIZE_X)] for _ in range(self.BOARD_SIZE_Y)]
        self.current_player = 1
        self.player_lost = None
        self.square_found = None
        self.moves_count = 0

    def check_for_draw(self):
        # Check if all the cells are filled, but no player has lost.
        return self.player_lost is None and all(cell for row in self.board for cell in row)
    
    def get_state(self):
        return HipGameState(self.board, self.current_player, self.player_lost, self.square_found)