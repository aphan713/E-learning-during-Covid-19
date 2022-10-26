datasets = ['LearnPlatform', 'BroadbandNow']

## ============================================ ##
import importlib

datasets_dict = {}
for dataset_name_str in datasets:
    datasets_dict[dataset_name_str] = getattr(importlib.import_module('.' + dataset_name_str, __name__), dataset_name_str)