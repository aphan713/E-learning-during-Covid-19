# Models

## Baselines

Average the entire year of data for each district. Same model is used for all states.

This yields only ~173 rows, so we use k-fold Cross Validation to measure model performance.

### Test Score Baselines

Each baseline trains 4 Ridge regression models ($\alpha = 0.5$), one for each comination of 4th & 8th grade, math & reading test scores, using 5- and 10-fold cross-validation. We select the better performing of the two cross-validations (on the training set) and select the corresponding test results.

- ___Baseline 1___: Uses engagement data only. ([Model](Models.ipynb#baseline1_model) / [Results](Models.ipynb#baseline1_results))
- ___Baseline 2___: Uses locale type only. Outperformed Baseline 1. ([Model](Models.ipynb#baseline2_model) / [Results](Models.ipynb#baseline2_results))