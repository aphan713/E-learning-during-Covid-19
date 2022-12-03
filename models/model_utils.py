from sklearn import preprocessing
from sklearn.model_selection import cross_validate, GroupKFold
from sklearn.pipeline import make_pipeline
try:
    import torch
except ImportError:
    print('pytorch not installed - neural network models will not be available')

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import cm
import matplotlib.colors as mcolors

import pandas as pd
import numpy as np
from tqdm import tqdm

from datetime import datetime, timedelta
from functools import partial
from pathlib import Path
import random


PROCESSED_DATA_DIR_PATH = Path('.') / '..' / 'data' / 'processed_data'

INPUT_FEATURES = ['engagement;pct_access',
                  'engagement;engagement_index',
                  'districts;locale',
                  'districts;state',
                  'broadband;wired_over_25',
                  'broadband;avg_mbps', 
                  'broadband;frac_access', 
                  'broadband;lowest_price',
                  'districts;pct_black/hispanic',
                  'districts;pct_free/reduced',
                  'districts;pp_total_raw'
                 ]

TARGET_FEATURES = ['testscores;math_4_2022',
                   'testscores;math_8_2022',
                   'testscores;reading_4_2022',
                   'testscores;reading_8_2022',
                   'testscores;math_4_2019',
                   'testscores;math_8_2019',
                   'testscores;reading_4_2019',
                   'testscores;reading_8_2019',
                   #'testscores;sat_pct_2022', 
                   'testscores;sat_ebrw_2022',
                   'testscores;sat_math_2022', 
                   #'testscores;sat_total_2022',
                   #'testscores;sat_pct_2020', 
                   'testscores;sat_ebrw_2019',
                   'testscores;sat_math_2019', 
                   #'testscores;sat_total_2019',
                   #'testscores;sat_ebrw_2020', 
                   #'testscores;sat_math_2020',
                   #'testscores;sat_total_2020'
                  ]

ALL_DAYS = []
d = datetime(2020, 1, 1)
while d.year != 2021:
    ALL_DAYS.append(d.strftime('%Y-%m-%d'))
    d += timedelta(days=1)
    
def load_dataset(temporal=False):
    dataset = None
    
    ## Load state dataframes
    for state_data_path in tqdm(PROCESSED_DATA_DIR_PATH.glob('*.gz'), total=23):
        df = pd.read_pickle(state_data_path)

        df = df.drop(['districts;county_connections_ratio'], axis=1)

        ### Remap categorical anonymized range data into numeric values
        def remap_ranges(x, bins_dict):
            if pd.isna(x):
                return None
            else:
                return bins_dict[float(x.split(',')[0][1:])]

        bins_dict = {float(n): i for i, n in enumerate(range(4000, 34000, 2000))}
        df['districts;pp_total_raw'] = df['districts;pp_total_raw'].apply(partial(remap_ranges, bins_dict=bins_dict))

        bins_dict = {float(n) / 100: i for i, n in enumerate(range(0, 100, 20))}
        df['districts;pct_black/hispanic'] = df['districts;pct_black/hispanic'].apply(partial(remap_ranges, bins_dict=bins_dict))
        df['districts;pct_free/reduced'] = df['districts;pct_free/reduced'].apply(partial(remap_ranges, bins_dict=bins_dict))

        df_temp = df.groupby(['time', 'district_id']).first()

        columns_to_average = ['engagement;pct_access', 'engagement;engagement_index']
        columns_to_reset = ['products;Sector(s)', 'products;Primary Essential Function']

        df_temp[columns_to_average] = df.groupby(['time', 'district_id']).mean()[columns_to_average]
        df_temp[columns_to_reset] = None

        df = df_temp
        del df_temp

        if temporal:
            state_fill = dict(df.groupby(['district_id']).first()['districts;state'])
            district_fill = dict(df.groupby(['district_id']).first()['districts;locale'])

            ## Fill in empty days with linear interpolation of existing values
            new_index = pd.MultiIndex.from_product([ALL_DAYS, df.index.levels[1]])
            df = df.reindex(new_index)

            for district_id in df.index.levels[1]:
                df_temp = df.loc[(slice(None), district_id), :].interpolate()
                df_temp['districts;state'] = state_fill[district_id]
                df_temp['districts;locale'] = district_fill[district_id]
                df.loc[(slice(None), district_id), :] = df_temp

            if dataset is None:
                dataset = df.swaplevel()
            else:
                dataset = pd.concat([dataset, df.swaplevel()]).sort_index(level='district_id')
        else:
            for district_id in df.index.levels[1]:
                df_temp = df.loc[(slice(None), district_id), :]
                row = df_temp.iloc[0][INPUT_FEATURES + TARGET_FEATURES]
                row.loc[columns_to_average] = df_temp[columns_to_average].mean()
                row['n_days'] = len(df_temp)
                if dataset is None:
                    dataset = pd.DataFrame(row).T.reset_index(level=0)
                else:
                    dataset = pd.concat([dataset, pd.DataFrame(row).T.reset_index(level=0)])

    if not temporal:
        dataset = dataset.drop(['level_0'], axis=1)

        ## Load averaged engagement data
        df = pd.read_csv(PROCESSED_DATA_DIR_PATH / 'LearnPlatform_engage_district_wide.csv')
        df = df.drop(['state'], axis=1)
        df = df.set_index(['district_id'])
        df = df.rename(lambda col_name: 'engagement;{}'.format(col_name), axis=1)
        dataset = dataset.join(df)

    for l in ['City', 'Suburb', 'Rural', 'Town']:
        dataset['districts;locale_{}'.format(l.lower())] = dataset['districts;locale'].apply(lambda x: int(x == l))
    
    return dataset


def run_experiment(dataset, input_features_list, output_targets_list, 
                   model_type, n_splits=5,
                   scoring_metrics_list=None,
                   temporal=False):
    
    if scoring_metrics_list is None:
        scoring_metrics_list = ['r2', 'neg_root_mean_squared_error']
    
    # ## ensure cross validation respects states (i.e., all data from a given state is in either the
    # ## test or train split - so if a "California Suburb" district is in the training split, all 
    # ## "California Suburb" (and city/town/rural) districts would also be in the training split)
    # k_fold_groups = pd.factorize(dataset['districts;state'])[0]

    ## ensure cross validation respects state/locale combinations (i.e., all data from a given state 
    ## and locale type is in either the test or train split - so "California Suburb" can be in the
    ## training split and "California City" can be in the test split, but all "California Suburb"
    ## districts would be in the training split)
    if temporal:
        temp_dataset = dataset.groupby(['district_id']).first()
        k_fold_groups = pd.factorize(list(zip(list(temp_dataset['districts;state']), list(temp_dataset['districts;locale']))))[0]
    else:
        k_fold_groups = pd.factorize(list(zip(list(dataset['districts;state']), list(dataset['districts;locale']))))[0]

    results = []
    for target in output_targets_list:

        X = np.array(dataset[input_features_list]).astype(float)
        Y = np.array(dataset[[target]]).astype(float).squeeze(-1)
        if temporal:
            X = X.reshape((-1, len(ALL_DAYS), len(input_features_list)))
            Y = Y[list(range(0, len(Y), len(ALL_DAYS)))]

        if temporal:
            mask = np.logical_and(~np.isnan(Y), ~np.any(np.any(np.isnan(X), axis=-1), axis=-1))
        else:
            mask = np.logical_and(~np.isnan(Y), ~np.any(np.isnan(X), axis=-1))
        X = X[mask]
        Y = Y[mask]
        groups = k_fold_groups[mask]

        print('Dataset for {} has {} samples after filtering'.format(target, np.sum(mask)))

        if temporal:
            for i in range(X.shape[2]):
                scaler = preprocessing.StandardScaler()
                X[:, :, i] = scaler.fit_transform(X[:, :, i])
            X = torch.tensor(X).float()
            Y = torch.tensor(Y.reshape(-1, 1)).float()
            model = model_type
        else:
            model = make_pipeline(preprocessing.StandardScaler(), 
                                  model_type)

        kf_splits = GroupKFold(n_splits=n_splits)
        results_dict = cross_validate(model, X, Y, 
                                      cv=kf_splits, 
                                      groups=groups,
                                      scoring=scoring_metrics_list,
                                      return_train_score=True,
                                      return_estimator=True,
                                      error_score='raise')
        results.append((results_dict, target, scoring_metrics_list, (kf_splits, groups), X, Y))

    return results


def print_results(results,
                  splits=['train'], scoring_metrics_list=None):
    
    if scoring_metrics_list is None:
        scoring_metrics_list = ['r2', 'neg_root_mean_squared_error']
        
    for results_dict, target, *_ in results:
        d = {}
        for scoring_metric in scoring_metrics_list:
            for split in splits:
                m = '{}_{}'.format(split, scoring_metric)
                r = round(np.mean(results_dict[m]), 4)
                if scoring_metric.startswith('neg'):
                    r = -r
                    m = '{}_{}'.format(split, scoring_metric[4:])

                d[m] = {target: r}
        display(pd.DataFrame(d).T)
        if splits == ['test']:
            print('{}: {}'.format(target, d['test_root_mean_squared_error'][target]))
        
        
def plot_residuals(results, dataset=None):
    
    if dataset is not None:
        unique_states = dataset['districts;state'].unique()
        colors = []
        cmaps = ['Dark2', 'Set1', 'tab10']
        for c in cmaps:
            cmap = cm.get_cmap(c)
            colors.append(cmap(np.arange(0.0, 1.0, 1 / np.floor(len(unique_states) / len(cmaps)))))
        colors = np.vstack(colors)
        cmap = mcolors.LinearSegmentedColormap.from_list('combined_cmap', colors)

        state_color_map = dict(zip(unique_states, cmap(np.arange(0.0, 1.0, 1 / len(unique_states)))))
        locale_types = ['City','Suburb','Town','Rural']

        legend_elements = [Line2D([0], [0], marker='s', color='w', label=state,
                           markerfacecolor=color, markersize=15) for state, color in state_color_map.items()]
        
    for results_dict, target, *_, groups, X, Y in results:
        predictions = []
        ground_truth = []
        
        states = []
        locales = []

        for (_, test_index), model in zip(groups[0].split(X, groups=groups[1]), 
                                          results_dict['estimator']):
            predictions += list(model.predict(X[test_index]))
            ground_truth += list(Y[test_index])
            if dataset is not None:
                states += list(dataset['districts;state'].iloc[test_index])
                locales += list(dataset['districts;locale'].iloc[test_index])

        sort_indices = np.argsort(ground_truth)
        ground_truth = np.array(ground_truth)[sort_indices]
        predictions = np.array(predictions)[sort_indices]
        if dataset is not None:
            states = np.array(states)[sort_indices]
            locales = np.array(locales)[sort_indices]
                   
        indices = np.array(range(len(sort_indices)))

        fig, ax = plt.subplots(figsize=(16, 8))
        
        if dataset is not None:
            for locale_type in locale_types:
                for state, color in state_color_map.items():
                    mask = np.logical_and(locales == locale_type, states == state)
                    ax.scatter(indices[mask], 
                               ground_truth[mask], 
                               marker='${}$'.format(locale_type[0]),
                               color=color)
                    ax.scatter(indices[mask], 
                               predictions[mask], 
                               marker='.', 
                               color='black')  
        else:
            ax.scatter(indices, 
                       ground_truth, 
                       marker='.',
                       color='tab:blue', label='Ground Truth')
            ax.scatter(indices, 
                       predictions, 
                       marker='.', 
                       color='black', label='Predictions')  

        ax.set_title(target)
        if dataset is not None:
            ax.legend(handles=legend_elements)
        else:
            ax.legend()
        display(fig)
        plt.close();
        plt.close();
        
