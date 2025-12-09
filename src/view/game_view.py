from rich.prompt import Prompt
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel


class GameView:
    
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
    
    def _create_layout(self):
        layout = Layout()

        # Main split
        layout.split_column(
            Layout(name='main', size=10),
            Layout(name='prompt', size=5)
        )

        # Horizontal aufteilen
        layout['main'].split_row(
            Layout(name='location', ratio=3),
            Layout(name='inventory', ratio=1)
        )

    def show_welcome(self):
        self.console.clear()
        self.console.print(Panel(
            'Willkommen beim RagVenture',
            subtitle='NLP Lernsoftware ;-)',
            border_style='yellow',
            padding=(2, 2)
        ))

    def show_game(self, location, exits, items, inventory, commands):
        self.layout['location'].update(Panel(...))
        self.layout['inventory'].update(Panel(...))
        self.layout['prompt'].update(Panel(...))


    def get_command(self):
        return Prompt.ask('What?')

    def show_message(self, prompt):
        self.console.print(f'Antwort: {prompt}')
        # self.layout['prompt'].update(Panel(...))
    
    def show_list(self, title, data):
        if not data:
            self.console.print(f"[dim]Da ist nichts.[/dim]")
            return

        self.console.print(f'{title}')

        for item in data:
            self.console.print(item)
