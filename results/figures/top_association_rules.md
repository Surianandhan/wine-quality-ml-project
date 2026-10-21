# Top 10 association rules for quality=High (overall, sorted by lift)

| antecedents                                                                                                                              | consequents   |   support |   confidence |   lift |
|:-----------------------------------------------------------------------------------------------------------------------------------------|:--------------|----------:|-------------:|-------:|
| alcohol=High, citric acid=High, density=Low, fixed acidity=High, free sulfur dioxide=Low, total sulfur dioxide=Low, volatile acidity=Low | quality=High  |    0.05   |            1 | 1.2903 |
| free sulfur dioxide=Low, residual sugar=High, sulphates=High, total sulfur dioxide=Low                                                   | quality=High  |    0.075  |            1 | 1.2903 |
| citric acid=High, fixed acidity=High, residual sugar=High, total sulfur dioxide=Low, volatile acidity=Low                                | quality=High  |    0.0536 |            1 | 1.2903 |
| fixed acidity=High, residual sugar=High, total sulfur dioxide=Low, volatile acidity=Low                                                  | quality=High  |    0.0536 |            1 | 1.2903 |
| alcohol=High, citric acid=High, fixed acidity=High, free sulfur dioxide=Low, residual sugar=High, total sulfur dioxide=Low               | quality=High  |    0.0643 |            1 | 1.2903 |
| alcohol=High, fixed acidity=High, free sulfur dioxide=Low, residual sugar=High, total sulfur dioxide=Low                                 | quality=High  |    0.0643 |            1 | 1.2903 |
| citric acid=High, fixed acidity=High, free sulfur dioxide=Low, residual sugar=High, total sulfur dioxide=Low                             | quality=High  |    0.0714 |            1 | 1.2903 |
| fixed acidity=High, free sulfur dioxide=Low, residual sugar=High, total sulfur dioxide=Low                                               | quality=High  |    0.0714 |            1 | 1.2903 |
| alcohol=High, citric acid=High, fixed acidity=High, residual sugar=High, total sulfur dioxide=Low                                        | quality=High  |    0.0786 |            1 | 1.2903 |
| alcohol=High, fixed acidity=High, residual sugar=High, total sulfur dioxide=Low                                                          | quality=High  |    0.0786 |            1 | 1.2903 |

## Cross-check against Ma et al. (2024) Figs. 4-5 key attributes

- Attributes appearing in our mined rules: ['alcohol', 'citric acid', 'density', 'fixed acidity', 'free sulfur dioxide', 'residual sugar', 'sulphates', 'total sulfur dioxide', 'volatile acidity']
- Paper's flagged key attributes (alcohol, sulphates, volatile acidity, citric acid): ['alcohol', 'citric acid', 'sulphates', 'volatile acidity']
- Agreement: ['alcohol', 'citric acid', 'sulphates', 'volatile acidity']
- In our rules only: ['density', 'fixed acidity', 'free sulfur dioxide', 'residual sugar', 'total sulfur dioxide']
- In paper's figures only, not in our top rules: []
