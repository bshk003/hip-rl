import config
import pygame

class HipGameGraphics: 
    def __init__(self, screen, players):
        self.screen = screen

        self.BOARD_SIZE_X = config.BOARD_SIZE_X
        self.BOARD_SIZE_Y = config.BOARD_SIZE_Y
        self.CELL_SIZE = config.CELL_SIZE
        self.MARGIN = config.MARGIN

        self.WIDTH = self.BOARD_SIZE_X * self.CELL_SIZE + 2 * self.MARGIN
        self.HEIGHT = self.BOARD_SIZE_Y * self.CELL_SIZE + 2 * self.MARGIN

        self.BG_COLOR = config.BG_COLOR
        self.LINE_COLOR = config.LINE_COLOR
        self.HIGHLIGHT_COLOR = config.HIGHLIGHT_COLOR
        self.CIRCLE_RADIUS = config.CIRCLE_RADIUS
        self.PLAYER_COLORS = config.PLAYER_COLORS
        self.PLAYER_COLORS_LOST = config.PLAYER_COLORS_LOST
        
        # The new game button
        self.FONT = pygame.font.Font(config.FONT, config.FONT_SIZE)
        self.BUTTON_COLOR = config.BUTTON_COLOR
        self.BUTTON_TEXT_COLOR = config.BUTTON_TEXT_COLOR
        self.BUTTON_TEXT_SURF = self.FONT.render('New Game', True, self.BUTTON_TEXT_COLOR)

        text_rect = self.BUTTON_TEXT_SURF.get_rect(center = (self.WIDTH // 2, self.MARGIN // 2))
        self.BUTTON_RECT = text_rect.inflate(30, 10) # Paddings around the text.

        # The message box (lost player or draw)
        self.MSGBOX_TEXT_COLOR = config.MSGBOX_TEXT_COLOR
        self.MSGBOX_COLOR = config.MSGBOX_COLOR
        self.MSGBOX_BORDER_COLOR = config.MSGBOX_BORDER_COLOR    
        self.MSGBOX_RECT = config.MSGBOX_RECT

        # Player names
        self.PLAYER_NAMES = {key: players[key].player_name for key in sorted(players.keys())}  

        self.BOARD_ELEMENTS = [self._draw_new_game_button, 
                               self._draw_grid, 
                               self._draw_disks, 
                               self._draw_message_box,
                               self._draw_player_names]  

        self.screen.fill(self.BG_COLOR)


    def _draw_new_game_button(self, game_state):
        # Draw a 'New Game' button
        pygame.draw.rect(self.screen, self.BUTTON_COLOR, self.BUTTON_RECT)
        pygame.draw.rect(self.screen, self.LINE_COLOR, self.BUTTON_RECT, width=2) 
        text_blit_rect = self.BUTTON_TEXT_SURF.get_rect(center=self.BUTTON_RECT.center)
        self.screen.blit(self.BUTTON_TEXT_SURF, text_blit_rect)

    def _draw_grid(self, game_state):
        # Draw grid
        for i in range(self.BOARD_SIZE_Y + 1):
            pygame.draw.line(self.screen, self.LINE_COLOR,
                             (self.MARGIN, self.MARGIN + i * self.CELL_SIZE),
                             (self.MARGIN + self.BOARD_SIZE_X * self.CELL_SIZE, self.MARGIN + i * self.CELL_SIZE), 2)
        for j in range(self.BOARD_SIZE_X + 1):
            pygame.draw.line(self.screen, self.LINE_COLOR,
                             (self.MARGIN + j * self.CELL_SIZE, self.MARGIN),
                             (self.MARGIN + j * self.CELL_SIZE, self.MARGIN + self.BOARD_SIZE_Y * self.CELL_SIZE), 2)

    def _draw_disks(self, game_state):
        # Draw disks
        for y in range(self.BOARD_SIZE_Y):
            for x in range(self.BOARD_SIZE_X):
                if game_state.board[y][x]:
                    color = self.PLAYER_COLORS[game_state.board[y][x]]
                    center = (self.MARGIN + x * self.CELL_SIZE + self.CELL_SIZE // 2,
                              self.MARGIN + y * self.CELL_SIZE + self.CELL_SIZE // 2)
                    pygame.draw.circle(self.screen, color, center, self.CIRCLE_RADIUS)
                    pygame.draw.circle(self.screen, self.LINE_COLOR, center, self.CIRCLE_RADIUS, width=2)
    
   
    def _draw_message_box(self, game_state):
        # Put up a message box if the game is over (player_lost != None). 
        # Highlight a losing square if it's not a draw.
        if game_state.player_lost:
            square_vertices = []
            for (x, y) in game_state.square_found:
                center = (self.MARGIN + x * self.CELL_SIZE + self.CELL_SIZE // 2,
                          self.MARGIN + y * self.CELL_SIZE + self.CELL_SIZE // 2)
                color = self.PLAYER_COLORS_LOST[game_state.player_lost]
                pygame.draw.circle(self.screen, color, center, self.CIRCLE_RADIUS)
                pygame.draw.circle(self.screen, self.HIGHLIGHT_COLOR, center, self.CIRCLE_RADIUS, width=3)
                square_vertices.append(center)
            
            # Highlight the square found.
            pygame.draw.polygon(self.screen, self.HIGHLIGHT_COLOR, square_vertices, width=3)
            
            pygame.draw.rect(self.screen, self.MSGBOX_COLOR, self.MSGBOX_RECT)
            pygame.draw.rect(self.screen, self.MSGBOX_BORDER_COLOR, self.MSGBOX_RECT, width=2)
            lost_text = self.FONT.render(f'{self.PLAYER_NAMES[game_state.player_lost]} lost', True, self.MSGBOX_TEXT_COLOR)
            text_rect = lost_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            
            self.screen.blit(lost_text, text_rect)

        elif game_state.player_lost == 0: # A draw
            pygame.draw.rect(self.screen, self.MSGBOX_COLOR, self.MSGBOX_RECT)
            pygame.draw.rect(self.screen, self.MSGBOX_BORDER_COLOR, 
                             self.MSGBOX_RECT, 
                             width=2)
            draw_text = self.FONT.render('Draw', True, self.MSGBOX_TEXT_COLOR)
            text_rect = draw_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            self.screen.blit(draw_text, text_rect)

    def _draw_player_names(self, game_state):
        # Draw player names at the bottom of the screen.
        cum_width = 0
        for i, player_name in self.PLAYER_NAMES.items():
            text_surf = self.FONT.render(player_name, True, self.PLAYER_COLORS[i])
            text_rect = text_surf.get_rect(midleft=(self.MARGIN + cum_width,
                                                    self.HEIGHT - self.MARGIN // 2))
            cum_width += text_rect.width + 20
            self.screen.blit(text_surf, text_rect)

    def draw_board(self, game_state):
        self.screen.fill(self.BG_COLOR)
        for element in self.BOARD_ELEMENTS:
            element(game_state)

        pygame.display.flip()
    
    def save_screenshot(self, filename):
        self.screen.fill(self.BG_COLOR) 
        self.draw_board() 
        # Save the screenshot
        pygame.image.save(self.screen, filename)
        print(f'A screenshot saved as {filename}')

    def get_cell(self, pos):
        mx, my = pos
        if not (self.MARGIN <= mx < self.MARGIN + self.BOARD_SIZE_X * self.CELL_SIZE and
                self.MARGIN <= my < self.MARGIN + self.BOARD_SIZE_Y * self.CELL_SIZE):
            return None
        x = (mx - self.MARGIN) // self.CELL_SIZE
        y = (my - self.MARGIN) // self.CELL_SIZE
        return (x, y)

    def get_clicked_element(self, pos):
        if self.BUTTON_RECT.collidepoint(pos):
            return ('new_game_button', None)
        cell = self.get_cell(pos)
        if cell is not None:
            return ('cell', cell)
        return (None, None)

    
 
    