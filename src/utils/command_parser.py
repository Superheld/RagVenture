

class CommandParser:
    
    def parse(self, input_text):
        """
        Parst einen Textinput
        
        Returns:
            dict: {'action': str, 'target': list, 'raw': str}
        """
        if not input_text:
            return {'action': None, 'target': None, 'raw': input_text}
        
        words = input_text.lower().strip().split()

        action = words[0]
        target = words[1]

        return {'action': action, 'targets': target, 'raw': input_text}
