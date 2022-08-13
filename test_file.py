# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13NcD8TZs8fJpXm-BPlO7t0m-z9jBgEdv
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
# %matplotlib inline

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer

from sklearn.preprocessing import OneHotEncoder


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from sklearn.metrics import precision_recall_fscore_support as score
from hyperopt import tpe, STATUS_OK, Trials, hp, fmin, space_eval


from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import log_loss

from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.feature_selection import f_classif
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn import metrics
from scipy import stats
import statsmodels.api as sm
import math
import re
from scipy import sparse

from sklearn.linear_model import LogisticRegression

import xgboost
from sklearn.metrics import roc_auc_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import plot_confusion_matrix

from xgboost import XGBClassifier

from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV

from sklearn import preprocessing
from tqdm.notebook import tqdm

from sklearn.metrics import precision_recall_fscore_support as score
from hyperopt import tpe, STATUS_OK, Trials, hp, fmin, space_eval

#pip install scikit-optimize
#pip install lightgbm

import nltk
nltk.download('stopwords')
nltk.download('wordnet')

#Loading Dataset
df = pd.read_csv('/content/drive/MyDrive/Kaggle_comps/train.csv')

df.head()

d_type = df['discourse_type'].to_list()
len(set(d_type))

#Checking for null values
df['discourse_effectiveness'].isnull().sum()

df['discourse_effectiveness'].value_counts()

#Checking for dataset imbalance
df.groupby('discourse_effectiveness').count().plot(kind ='bar')

#Using Word Lemmatizer
nltk.download('omw-1.4')

wordnet = WordNetLemmatizer()

def clean(text):
    text="".join([re.sub('[^a-zA-Z]',' ',char) for char in text])
    text=text.lower()
    text=text.split()
    text=[wordnet.lemmatize(word) for word in text if word not in set(stopwords.words("english"))]
    text=" ".join(text)
    return text

#Defining a function to preprocess both train and test data.
def data_preprocess(f):
  df = pd.read_csv(f)
  df = df.fillna('')
  df['discourse_text'] = df['discourse_text'].apply(clean)
  X = df['discourse_text'].values
  return X

X_train = data_preprocess('/content/drive/MyDrive/Kaggle_comps/train.csv')
X_test = data_preprocess('/content/drive/MyDrive/Kaggle_comps/test.csv')


n = pd.DataFrame(X_train)


M = np.concatenate((X_train,X_test))
M.shape

le = preprocessing.LabelEncoder()
le.fit(list(set(d_type)))
df['type'] = le.transform(df['discourse_type'])

df.head()

df_train = pd.read_csv('/content/drive/MyDrive/Kaggle_comps/train.csv')
df_test = pd.read_csv('/content/drive/MyDrive/Kaggle_comps/test.csv')

X_type_train = pd.get_dummies(df_train, columns=["discourse_type"])
X_type_test = pd.get_dummies(df_test, columns=["discourse_type"])

discourse_type = ['discourse_type_'+x for x in list(set(d_type))]
discourse_type

df_test

discourse_type_test = list(set(df_test['discourse_type'].to_list()))
for d in discourse_type:
  if d not in discourse_type_test:
    X_type_test[d] = 0*pd.Series(range(len(df_test)))

X_type_train = X_type_train[discourse_type]
X_type_test = X_type_test[discourse_type]

X = np.concatenate((X_train,X_test))
X.shape

#Converting the textual data into numerical data using vertorizer
#vectorizer = TfidfTransformer(max_features = 1000)
vectorizer = TfidfVectorizer(max_features = 1500)
vectorizer.fit(X)

X = vectorizer.transform(X)

print(X.shape)

X_type = np.concatenate((X_type_train, X_type_test), axis = 0)
X_type = sparse.csr_matrix(X_type)

print(X_type.shape)

X_mod = sparse.hstack((X,X_type))

le = preprocessing.LabelEncoder()
y_type = df['discourse_effectiveness']
le.fit(list(set(y_type)))
df['y_trans'] = le.transform(df['discourse_effectiveness'])

L = len(df)
y = df['y_trans'].values
df.head()
X = X_mod.tocsr()[:L]

model_xgboost = xgboost.XGBClassifier(n_estimators = 100,
                                     eval_metric = 'logloss')

kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

score = cross_val_score(model_xgboost, X, y, cv =kfold)

print("The mean validaiton score on 10 fold CV is : {:.4f}\nThe standard deviation of the spread is : {:.4f} "
      .format(score.mean(),score.std()))

#feature importance
model_xgboost.fit(X,y)
sorted_features = sorted(model_xgboost.feature_importances_)
print(sorted_features)
# plot
plt.bar(range(len(sorted_features)), sorted_features)
plt.show()



"""Grid search

"""

classifier = XGBClassifier()

params2 = {
    "learning_rate" : [0.1, 0.25, 0.5, 0.7, 0.8, 1],
    "max_depth" : [3, 5, 7, 10, 13],
    "min_child_weight" : [4, 5, 7, 9, 10,13],
    "gamma" : [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],

    "colsample_bytree" : [ 0.3, 0.4, 0.5, 0.7, 0.8, 1],
    "subsample " :[0.4, 0.6, 0.75, 0.8, 1]


}

grid_search = GridSearchCV(
    estimator = classifier, param_grid = params2, scoring ="accuracy", n_jobs =-1, cv=10, verbose =3)

grid_search = grid_search.fit(X,y)

grid_params = grid_search.best_params_

#Fitting the model with the best params we got
classifier = xgboost.XGBClassifier(**grid_params)

#Using Stratified Kfold validation for accuracy
skf = StratifiedKFold(n_splits=10)

score_g = cross_val_score(classifier, X_train, y, cv =skf, scoring = 'accuracy')

print("The mean validaiton score on 10 fold CV using GridSearchCV : {:.4f}\nThe standard deviation of the spread is : {:.4f} "
      .format(score_g.mean(),score_g.std()))

"""Checking for overfitting"""

#Change the parameters in classifier to fit the hyperparameters from GridSearchcv
skf = StratifiedKFold(n_splits=10)

mae_train = []
mae_test = []
acc_train = []
acc_test = []
for train_index, test_index in tqdm(skf.split(X,y)):
  X_train, X_test = X[train_index], X[test_index]
  y_train, y_test = y[train_index], y[test_index]
  # X_train, X_test = X.iloc[train_index].to_numpy(), X.iloc[test_index].to_numpy()
  # y_train, y_test = y.iloc[train_index].to_numpy().ravel(), y.iloc[test_index].to_numpy().ravel()
  model = xgboost.XGBClassifier(**grid_params)
  model.fit(X_train, y_train)
  y_train_pred = model.predict(X_train)
  y_test_pred = model.predict(X_test)
  acc_train.append(model.score(X_train,y_train))
  acc_test.append(model.score(X_test,y_test))
  mae_train.append(mean_absolute_error(y_train, y_train_pred))
  mae_test.append(mean_absolute_error(y_test, y_test_pred))

#Plotting the scores with MAE to check for overfitting
folds = range(1, skf.get_n_splits() + 1)
plt.plot(folds, mae_train, 'o-', color='green', label='train')
plt.plot(folds, mae_test, 'o-', color='red', label='test')
plt.legend()
plt.grid()
plt.xlabel('Number of fold')
plt.ylabel('Mean Absolute Error')
plt.show()

#Plotting the scores with accuracy to check for overfitting
folds = range(1, skf.get_n_splits() + 1)
plt.plot(folds, acc_train, 'o-', color='green', label='train')
plt.plot(folds, acc_test, 'o-', color='red', label='test')
plt.legend()
plt.grid()
plt.xlabel('Number of fold')
plt.ylabel('Accuracy')
plt.show()



"""Bayesian Optimization"""

# Space
space = {
    'learning_rate': hp.choice('learning_rate', [ 0.01, 0.1, 0.25, 0.5, 1]),
    'max_depth' : hp.choice('max_depth', [3,5,7, 9, 10,13]),
    'min_child_weight' : hp.choice('min_child_weight', range(1,14)),
    'gamma' : hp.choice('gamma', [i/10.0 for i in range(0,10)]),
    'colsample_bytree' : hp.choice('colsample_bytree', [i/10.0 for i in range(2,11)]),
    'subsample' :[0.4, 0.6, 0.75, 0.8, 1]

    #'reg_alpha' : hp.choice('reg_alpha', [0, 1e-5, 1e-2, 0.1, 1, 10, 100]),
    #'reg_lambda' : hp.choice('reg_lambda', [1e-5, 1e-2, 0.1, 1, 10, 100])
}
# Set up the k-fold cross-validation
kfold = StratifiedKFold(n_splits=5)
# Objective function
def objective(params):

    xgboost = XGBClassifier(seed=42, **params)
    scores = cross_val_score(xgboost, X, y, cv=kfold, scoring='accuracy', n_jobs=-1)
    # Extract the best score
    best_score = max(scores)
    # Loss must be minimized
    loss = - best_score
    # Dictionary with information for evaluation
    return {'loss': loss, 'params': params, 'status': STATUS_OK}
# Trials to track progress
bayes_trials = Trials()
# Optimize
best = fmin(fn = objective, space = space, algo = tpe.suggest, max_evals = 100, trials = bayes_trials)


# Print the values of the best parameters
print(space_eval(space, best))

#Fitting the model with the best params we got
classifier = xgboost.XGBClassifier(min_child_weight= 1,
  max_depth= 9,
  learning_rate= 0.5,
  gamma= 0.1,
  colsample_bytree= 1,
  n_estimators = 100,eval_metric = 'auc')

#Using Stratified Kfold validation for accuracy
skf = StratifiedKFold(n_splits=10)
score_b = cross_val_score(classifier, X_train, y, cv =skf, scoring = 'accuracy')

print("The mean validaiton score on 10 fold CV using GridSearchCV : {:.4f} \nThe standard deviation of the spread is : {:.4f}"
      .format(score_b.mean(),score_b.std()))
