# Models

## Baselines

Average the entire year of data for each district. Same model is used for all states.

This yields only ~173 rows, so we use k-fold Cross Validation to measure model performance. _Note that the folds are constructed to ensure that all data from a given state is in either the test or train split._

### Test Score Baselines

Each baseline trains 4 Ridge regression models ($\alpha = 0.5$), one for each comination of 4th & 8th grade, math & reading test scores, using 5- and 10-fold cross-validation. We select the better performing of the two cross-validations (on the training set) and select the corresponding test results.

- ___Baseline 1___: Uses engagement data only. ([Model](Models.ipynb#baseline1_model) / [Results](Models.ipynb#baseline1_results))
- ___Baseline 1a___: Uses average engagement data only, split into product types. Performed comparably to Baseline 1. ([Model](Models.ipynb#baseline1a_model) / [Results](Models.ipynb#baseline1a_results))
- ___Baseline 1b___: Uses median engagement data only, split into product types. Outperformed by Baselines 1 and 1a. ([Model](Models.ipynb#baseline1b_model) / [Results](Models.ipynb#baseline1b_results))
- ___Baseline 2___: Uses locale type only. Outperformed Baseline 1. ([Model](Models.ipynb#baseline2_model) / [Results](Models.ipynb#baseline2_results))
- ___Baseline 3___: Uses broadband data only. Outperformed by Baseline 1. ([Model](Models.ipynb#baseline3_model) / [Results](Models.ipynb#baseline3_results))

### Other Test Score Models

- ___Decision Tree 1___: Uses average engagement data (split into product types) along with locale type and broadband data. Worse than baseline models. ([Model](Models.ipynb#tree1_model) / [Results](Models.ipynb#tree1_results))