class CommandParser:
    
    def parse(self, input_text):
        """
        Parst einen Textinput
        
        Returns:
            dict: {'action': str, 'targets': list, 'raw': str}
        """
        if not input_text or not input_text.strip():
            return {'action': None, 'targets': [], 'raw': input_text}
        
        words = input_text.lower().strip().split()

        action = words[0]
        targets = words[1:]

        return {'action': action, 'targets': targets, 'raw': input_text}
