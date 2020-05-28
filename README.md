# Recommendation System

Recommend businesses to users based on [Yelp Dataset](https://www.yelp.com/dataset).

## Installation

Install Miniconda **(preferred)** or Anaconda [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/macos.html).

Create a new python environment with `requirements.txt`.

```
conda create -n rec_sys --file requirements.txt
```

Activate the `rec_sys` environment.

```
source activate rec_sys
```

**Note**: The `requirements.txt` may not contain all required packages. Please use `conda install` if there is any missing package.

## Documentations

[Data Viewer](https://github.com/zhudhjen/yelp-recommendation-system/tree/master/data_viewer)

[Sentiment Analyzer](https://github.com/zhudhjen/yelp-recommendation-system/tree/master/sentiment_analyzer)

[Visualization](https://github.com/zhudhjen/yelp-recommendation-system/tree/master/visualization)

## Evaluation

- RMSE
- ROC AUC
- Precision-at-K (optional)
