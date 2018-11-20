# Yelp Recommendation System

Recommend new restaurants to customers according to [Yelp Dataset](https://www.yelp.com/dataset/challenge).

**Note**: If you need to add some codes or docs or even directories only used by yourself in the repo, please modify things in `.git/info/exclude` instead of `.gitignore`.

## Installation

Install Miniconda **(preferred)** or Anaconda [here](https://conda.io/docs/user-guide/install/macos.html).

Create a new python environment with `requirements.txt`.

```
conda create -n rec_sys --file requirements.txt
```

Activate the `rec_sys` environment.

```
source activate rec_sys
```

**Note**: The `requirements.txt` may not contain all required packages. Please use `conda install` if there is any missing package.

## Data Viewer

[Doc](https://github.com/zhudhjen/yelp-recommendation-system/tree/master/data_viewer)

## Sentiment Analyzer

[Doc](https://github.com/zhudhjen/yelp-recommendation-system/tree/master/sentiment_analyzer)

## Evaluation

- RMSE
- ROC AUC
- Precision-at-K (optional)

## Links

[Proposal](https://docs.google.com/document/d/12MQUmbk-Ioh7L3wukDj7LEOFFX_jXR6YvxfCKi6jSwk/edit)

[Updates](https://docs.google.com/document/d/1hjC-rEDI9wovttoo9SyrPneD1aTt512K5kQDevwL0Xg/edit?usp=sharing)
