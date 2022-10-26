from data import Dataset



if __name__ == "__main__":
    dataset = Dataset(['BroadbandNow', 'LearnPlatform'])
    
    print(dataset.LearnPlatform.engagement_dataframes_dict['1000'].head())
    print(dataset.BroadbandNow.broadband_dataframe.head())