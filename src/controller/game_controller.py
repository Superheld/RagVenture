
import logging
from view.game_view import GameView
from model.game_model import GameModel
from utils.smart_parser import SmartParser
from utils.embedding_utils import EmbeddingUtils

class GameController:

    def __init__(self):
        
        self.view = GameView()
        self.model = GameModel()
        self.parser = SmartParser()
        
        self.embedding_utils = EmbeddingUtils()
        
        self.game_state = {}
        self.game_running = False

        logging.basicConfig(
            filename='parser_debug.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )

    def _update_game_state(self):

        self.game_state = {
            'location': self.model.current_location(),
            'items': self.model.location_content(),
            'exits': self.model.location_exits(),
            'inventory': self.model.player_inventory()
        }
        
        logging.info(f"State: {self.game_state}")
        self.view.update_panels(**self.game_state)

    def run_game(self):
        self.game_running = True

        self.view.show_welcome()
        input()
        self._update_game_state()

        self.view.refresh()

        while self.game_running:
            user_input = self.view.get_input()
            status = self.process_input(user_input)
            self._update_game_state()
            self.view.refresh(status=status)
    
    def process_input(self, input):

        if input == 'quit':
            self.game_running = False
            return "Auf Wiedersehen!"

        parsed = self.parser.parse(input)

        verb = parsed[0]['verb']
        noun = parsed[0]['noun']

        command = self.embedding_utils.verb_to_command(verb)
        
        if command['best_command'] == 'go':

            if not noun:
                return f"Wohin genau?"
            else:
                # Ziel finden
                possible_targets = self.game_state['exits']
                logging.info(f"LOCATION: {possible_targets}")
                target = self.embedding_utils.match_entities(noun, [t for t in possible_targets])

                result = self.model.move_player(target[0]['id'])

                if result:
                    return f'Du bist jetzt in {result[0]['name']}'
                else:
                    return 'Ups, gestolpert.'

#        elif command['best_command'] == 'take':
#            if not target:
#                result = self.model.location_item()
#                return"Was genau?"
#
#            else:
#                result = self.model.take_item(target[0])
#                
#                if result:
#                    return f'Du trägst jetzt {result[0]['i.name']}'
#
#        elif command['best_command'] == 'drop':
#            if not target:
#                result = self.model.player_inventory()
#                return "Fallengelassen sag ich mal"
#
#            else:
#                result = self.model.drop_item(target[0])
#                
#                if result:
#                    return f'Du hast {result[0]['i.name']} abgelegt.'

        else:
            return f"Das konnte nicht entschlüsselt werden."