# Models

## Requirements

- sklearn
- matplotlib
- pandas
- numpy
- tqdm

_If running the RNN:_

- pytorch
- skorch (https://github.com/skorch-dev/skorch)

## Functions

__```load_dataset```__```(temporal=False)```

Loads all data from ```../data/processed_data``` into a unified Pandas DataFrame.

_PARAMETERS:_
- ```temporal``` (bool): If ```False``` (default), temporal data will be averaged by district (i.e., the resulting DataFrame will be indexed by district ID alone. IF ```True```, temporal data will be preserved (and any missing values from 2020 linearly interpolated from their neighbors), with the resulting DataFrame indexed by both date and district ID.

_RETURNS:_
- ```dataset``` (Pandas DataFrame): Combined, filtered, and processed dataset.

-----------

__```run_experiment```__```(dataset, input_features_list, output_targets_list, model_type, n_splits=5, scoring_metrics_list=None, temporal=False)```

Trains a model for each target variable using the provided data and input features, with k-fold cross-validation.

Note that the cross-validation respects state/locale combinations (i.e., all data from a given state and locale type is in either the test or train split - so "California Suburb" can be in the training split and "California City" can be in the test split, but all "California Suburb" districts would be in the training split).

_PARAMETERS:_
- ```dataset``` (Pandas DataFrame): (See the output of __```load_dataset```__ above)
- ```input_features_list``` (list of strings): Column names from ```dataset``` that will be fed into the model as input features.
- ```output_targets_list``` (list of strings): Column names from ```dataset``` that will serve as target variables.
- ```model_type``` (Estimator object): An instantiated object implementing the sklearn [estimator interface](https://scikit-learn.org/stable/developers/develop.html) (i.e., ```fit```, ```predict```, etc.). Nearly every sklearn model implements this by default, and for pytorch models, skorch (see above) can be used to wrap the model in an estimator interface.
- ```n_splits``` (int): Number of splits in the k-fold cross-validation.
- ```scoring_metrics_list``` (list of strings): List of scoring functions to evaluate. See https://scikit-learn.org/stable/modules/model_evaluation.html (section 3.3.1.1, first column) for possible values.
- ```temporal``` (bool): If ```False``` (default), model input will be one-dimensional for each sample (i.e., a vector of feature values). If ```True```, model input for each sample will be a two-dimensional tensor, where the first dimension is sequence length and the second is feature values. Should match ```temporal``` in __```load_dataset```__.

_RETURNS:_
- ```results``` (list of tuples): A list of tuples, one tuple for each target variable, each tuple with various model outputs. The tuple includes:
 - [0]: The ```scores``` dictionary, as described in the sklearn [cross-validation documentation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.cross_validate.html?highlight=cross_validate#sklearn.model_selection.cross_validate).
 - [1]: The name of the target variable for this particular model (string).
 - [2]: The metrics used to evaluate this model (list of strings).
 - [3]: A tuple of ```(kf_splits, groups)```, where ```kf_splits``` is a [GroupKFold object](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html?highlight=groupkfold#sklearn.model_selection.GroupKFold) used to initialize the cross-validation splits and ```groups``` are the assignments of each sample to each group to ensure consistency of states/locales as described above.
 - [4]: The numpy array of input values. Note that in the ```temporal=False``` case, these are not normalized (but in both the ```temporal=False``` and ```temporal=True``` cases, X _will_ be normalized with standard deviation 1 and mean 0 before being fed into the model).
 - [5]: The numpy array of target values.
 
-----------

__```print_results```__```(results, splits=['train'], scoring_metrics_list=None)```

Prints formatted results.

_PARAMETERS:_
- ```results``` (list of tuples): (See the output of __```run_experiment```__ above)
- ```splits``` (list of strings): List of strings (either ```train```, ```test```, or both) of names of data splits to print metrics over.
- ```scoring_metrics_list``` (list of strings): List of scoring functions to evaluate. See https://scikit-learn.org/stable/modules/model_evaluation.html (section 3.3.1.1, first column) for possible values. Each metric printed must have also been specified in the call to __```run_experiment```__ above, but not all metrics from that call have to be printed.

_RETURNS:_
- _None_

-----------

__```plot_residuals```__```(results, dataset=None)```

Plots ground-truth vs. predicted values of the target variables in ```results```.

_PARAMETERS:_
- ```results``` (list of tuples): (See the output of __```run_experiment```__ above)
- ```dataset``` (Pandas DataFrame): (See the output of __```load_dataset```__ above). If not ```None``` (default), the plot will visualize the state and locale type of each ground-truth data point.

_RETURNS:_
- _None_