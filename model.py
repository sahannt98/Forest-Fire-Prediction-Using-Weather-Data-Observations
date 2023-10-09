from joblib import load
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import ExtraTreesClassifier
from catboost import CatBoostClassifier, Pool
from sklearn.ensemble import VotingClassifier

def get_prediction():
    load_model = load("ensemble.joblib")
    return load_model

get_prediction()