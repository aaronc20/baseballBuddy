from src.models.statisticSplits.split import Split

mapping = {
    'a': 'away',
    'h': 'home',
    'vl': 'vL',
    'vr': 'vR',
}

class CareerStatSplits(Split):
    def __init__(self, splits, group):
        super().__init__(splits)

        self.split_data = self.splits

    def get_split_data(self):
        return self.split_data['stat']
    
    def get_short_name(self):
        
        split = mapping[self.split_data['split']['code']]
        return f"career {split}"


            
            



        


