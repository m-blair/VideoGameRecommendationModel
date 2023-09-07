# Video Game Recommendation Model (VGRM)
A video game recommendation model trained using self-curated data from IGDB, making use of their REST API and python.
This project is a work in progress, and this repo is meant to document the entire process of creating a machine learning model *mostly* from scratch, including building our own dataset to be used in training testing, and validating the model. 

For this model, we are using a _Content-Based Filtering approach_, where we feed the model data containing features video game titles, rather than feeding it user preference data. This methodology has its pros and cons, but ultimately was chosen due to the relative ease of access to game content data over user preference data. The goal for this model is for a user to provide the name of a video game title, and the model will respond with a short list of titles most similar to it. Obviously, this is quite limited as it doesn't factor in a user's preferences or games they've previously enjoyed. Eventually we will shift our methodology to more of a mixed-filtering Approach, by allowing the user to provide some preferential information which influences the model's recommendations, and present various options and configurations for how to present the recommendations, which may remedy the disadvantages of a solely Content-Based filtering approach. 



# Current Status:
We are in the process of expanding the game library which will be used in model training. So far, we have created a data pipeline to and from the external data source (IGDB), and defined a procedure for preprocessing the resulting data. We have performed a baseline analysis of the data obtained so far (roughly 5000 titles), identified the most viable features, as well as the different encoding methods we will use in translating this data for the model to use. By the end of this section of the project, we hope to have accrued a dataset of at least 10000 titles, and their various selected features.
___

# Project Outline:

## Curating the dataset
- define a base set of video game titles to find data for, using a dataset from kaggle [here](https://www.kaggle.com/datasets/gregorut/videogamesales)
- pull data on each title and store in a csv representing the 'game library'
- preprocess/clean the stored data

## Feature Selection
- perform exploratory analysis on the game library, identify underlying trends in the data
- identify best features to utilize (genres, themes, summary, ...)
  
## Feature Encoding
- determine best methods for encoding each of the selected features from previous section
- choose a similarity metric (cosine similarity)
- calculate normalized similarity scores for each feature
- determine/fine-tune weights for each feature (how much each feature contributes the the overall similarity score)
- aggregate/calculate similarity scores pairwise

## Model Instantiation/Training
- design the network layout for the model
- define process of model training/testing/validation
- train model on split datasets based off of game library
- test the model (a lot)
- examine performance & perform model diagnostic checks

## Optimization
- using the results of the previous step, identify possible improvements to the model at various stages

## Develop a GUI
- use pygame + tkinter to develop a front-end interface for inputting data into the model and viewing results 
___


Sources:

* [Data Source (IGDB)](https://www.igdb.com/)

* [Game Titles (Kaggle)](https://www.kaggle.com/datasets/gregorut/videogamesales)

