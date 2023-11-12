class Settings:
    def __init__(self, gamma: float, num_steps: int):
        self.gamma = gamma
        self.num_steps = num_steps
        self.colorScheme = {
            'regular': {
                'good': 'rgb(0, 255, 0)', 
                'bad': 'rgb(255, 0, 0)'
            },
            'accessible': {
                'good': 'rgb(0, 0, 255)', 
                'bad': 'rgb(255, 0, 255)', 
            } 
        }