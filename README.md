# Recommendation System with Aspect-Based Sentiment Analysis

Recommend businesses to users based on [Yelp Dataset](https://www.yelp.com/dataset/challenge).

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

## Documentations

[Data Viewer](https://github.com/zhudhjen/yelp-recommendation-system/tree/master/data_viewer)

[Sentiment Analyzer](https://github.com/zhudhjen/yelp-recommendation-system/tree/master/sentiment_analyzer)

## Evaluation

- RMSE
- ROC AUC
- Precision-at-K (optional)

## Links

* [Yelp Dataset](https://www.yelp.com/dataset/challenge)
* [Proposal](https://docs.google.com/document/d/12MQUmbk-Ioh7L3wukDj7LEOFFX_jXR6YvxfCKi6jSwk/edit)
* [Data](https://drive.google.com/open?id=1v-ayr_m-0MUgviN6pulnRzdn-5hx9oQC)

## Contributions

### Qiming Du

* Data Viewer (a SQLite database built from Yelp Dataset for easy data exploration)
* Sentiment Analyzer (aspect-based sentiment analysis on review text)

### Dinghan Zhu

* LightFM Model Recommendation System 
* Spotlight Model Recommendation System
* Analyze and determine evaluation methods

### Wenjing Duan

* ItemBased & UserBased Recommendation System
* ModelBased Recommendation System
