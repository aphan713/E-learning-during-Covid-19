from pathlib import Path

import pandas as pd

from .generic_dataset import GenericDataset



class LearnPlatform(GenericDataset):
    def _load_data(self):
        """Loads LearnPlatform data from ./../raw_data/LearnPlatform.
        
        The engagement data is loaded into a dictionary, keyed by 
        school district IDs (i.e., csv file names)
        """
        print("Loading LearnPlatform data . . .")
        
        self._data_dir_path = (Path(__file__).parent / '..' / 'raw_data' / 'LearnPlatform').resolve()
        
        self.district_dataframe = pd.read_csv(self._data_dir_path / 'districts_info.csv')
        self.product_dataframe = pd.read_csv(self._data_dir_path / 'products_info.csv')
        
        self.engagement_dataframes_dict = {}
        for district_engagement_path in (self._data_dir_path / 'engagement_data').iterdir():
            self.engagement_dataframes_dict[district_engagement_path.stem] = \
                                pd.read_csv(district_engagement_path)
                           
        print("Done!")
            
            

if __name__ == "__main__":
    pass