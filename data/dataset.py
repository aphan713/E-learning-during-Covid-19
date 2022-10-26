from .datasets import datasets_dict



class Dataset:
    def __init__(self, datasets_to_load_list=None):
        if datasets_to_load_list is not None:
            for dataset_name_str in datasets_to_load_list:
                self.add_dataset(dataset_name_str)
                
                
    def add_dataset(self, dataset_name_str):
        try:
            setattr(self, dataset_name_str, datasets_dict[dataset_name_str]())
        except KeyError:
            raise NotImplementedError('Dataset {} not available'.format(dataset_name_str))
                