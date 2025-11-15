
from view.game_view import GameView
# from model.game_model import GameModel

class GameController:

    def __init__(self):
        self.view = GameView()
        self.running = False

    def run_game(self):
        self.running = True
        self.view.show_welcome()

        while self.running:
            command = self.view.get_command()
            self.process_command(command)
    
    def process_command(self, command):
        if command == 'quit':
            self.running = False
        else:
            self.view.answer(command)