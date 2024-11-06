import numpy as np
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.linear_model import HuberRegressor, SGDRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.svm import SVR


def build_time_series_split_cv_by_years(df_train, num_splits=4):
    df_train = df_train.set_index('year')
    years = np.sort(df_train.index.unique())

    tscv = TimeSeriesSplit(num_splits)
    cv = []
    for train_index, test_index in tscv.split(years):
        train_years, test_years = years[train_index], years[test_index]
        cv_train_index = np.where(df_train.index.isin(train_years))[0]
        cv_test_index = np.where(df_train.index.isin(test_years))[0]
        cv.append((cv_train_index, cv_test_index))
    return cv


def cross_validation(df_train, y_train, num_splits=4):

    cv = build_time_series_split_cv_by_years(df_train, num_splits)
    
    pipe = Pipeline([
        ('model', None)
    ])

    params = [
        {
            'model': [SGDRegressor(max_iter=1000)],
            'model__alpha': [0.0001, 0.001, 0.01, 0.1],
            'model__penalty': ['l1', 'l2', 'elasticnet'],
            'model__eta0': [0.0001, 0.001, 0.01]
        },
        {
            'model': [HuberRegressor(max_iter=1000)],
            'model__epsilon': [1.2, 1.35, 1.5, 2],
            'model__alpha': [0.0001, 0.001, 0.01, 0.1]
        },
        {
            'model': [DecisionTreeRegressor(random_state=4)],
            'model__max_depth': [5, 8, 10, 15],
            'model__min_samples_leaf': [3, 5, 8, 10]
        },
        {
            'model': [RandomForestRegressor(random_state=4)],
            'model__max_depth': [5, 8, 10, 15],
            'model__min_samples_leaf': [3, 5, 8, 10],
            'model__n_estimators': [10, 50, 100, 150]
        },
        {
            'model': [XGBRegressor(random_state=4)],
            'model__max_depth': [5, 8, 10, 15],
            'model__n_estimators': [10, 50, 100, 150],
            'model__eta': [0.3, 0.1]
        },
        {
            'model': [SVR()],
            'model__kernel': ['linear', 'rbf'],
            'model__C': [0.1, 1, 5, 15],
            'model__epsilon': [0.01, 0.1, 0.5, 1.0]
        }
    ]

    scoring_metric = 'neg_mean_squared_error'
    grid = GridSearchCV(pipe, params, cv=cv, scoring=scoring_metric, return_train_score=True)
    result = grid.fit(df_train, y_train)

    print(f"THE BEST MODEL IS:\n{result}")