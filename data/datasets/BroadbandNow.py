from pathlib import Path

import pandas as pd

from .generic_dataset import GenericDataset



class BroadbandNow(GenericDataset):
    def _load_data(self):
        """Loads BroadbandNow data from ./../raw_data/BroadbandNow.
        
        The engagement data is loaded into a dictionary, keyed by 
        school district IDs (i.e., csv file names)
        """
        print("Loading BroadbandNow data . . .")
         
        self._data_dir_path = (Path(__file__).parent / '..' / 'raw_data' / 'BroadbandNow').resolve()
        
        self.broadband_dataframe = pd.read_csv(self._data_dir_path / 'broadband_data_opendatachallenge.csv', encoding='ANSI')
        
        print("Done!")
            
            

if __name__ == "__main__":
    pass