import argparse
import pickle
import sys
import os
import pandas as pd
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.preprocessing import OneHotEncoder, RobustScaler, MinMaxScaler
from sklearn.linear_model import HuberRegressor
from sklearn.metrics import mean_squared_error, root_mean_squared_error
sys.path.append(os.getcwd())
from app.preprocessing import data_preprocessing_workflow


def load_dataset(input_file):
    return pd.read_csv(input_file)


def split_dataset(df, years_for_test=3):
    cols_to_keep = ['life_expectancy', 'year', 'status', 'adult_mortality', 'infant_mortality_rate',
                    'gdp', 'total_expenditure', 'income_composition_of_resources',
                    'polio', 'diphtheria', 'hiv_aids', 'thinness_5-9_years', 'thinness_10-19_years',
                    'alcohol', 'schooling']
    df_keep = df.loc[:, cols_to_keep]
    years_unique = df_keep.year.sort_values(ascending=False).unique()

    df_train = df_keep[df_keep.loc[:, 'year'] < years_unique[years_for_test - 1]]
    df_train.reset_index(drop=True, inplace=True)
    y_train = df_train['life_expectancy']
    df_train = df_train.drop('life_expectancy', axis=1)

    df_test = df_keep[df_keep.loc[:, 'year'] >= years_unique[years_for_test - 1]]
    df_test.reset_index(drop=True, inplace=True)
    y_test = df_test['life_expectancy']
    df_test = df_test.drop('life_expectancy', axis=1)
    
    return df_train, y_train, df_test, y_test


def train_onehot_encoder(df_train):
    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    encoder.fit(df_train['status'].to_numpy().reshape(-1, 1))
    return encoder


def train_data_imp(df_train):
    imp = IterativeImputer(max_iter=10, random_state=4)
    imp.fit(df_train)
    return imp


def train_data_scalers(df_train, y_train):
    cols_standard = ['gdp', 'total_expenditure', 'alcohol', 'schooling']
    cols_minmax = ['adult_mortality', 'infant_mortality_rate', 'polio', 'diphtheria', 'hiv_aids',
                   'thinness_5-9_years', 'thinness_10-19_years']
    Xstd = RobustScaler()
    Xstd.fit(df_train[cols_standard])
    ystd = RobustScaler()
    ystd.fit(y_train.to_numpy().reshape(-1, 1))
    Xnorm = MinMaxScaler()
    Xnorm.fit(df_train[cols_minmax])
    return Xstd, ystd, Xnorm


def train_preprocessing_workflow(df_train, y_train):
    encoder = train_onehot_encoder(df_train)
    imp = train_data_imp(df_train)
    Xstd, ystd, Xnorm = train_data_scalers(df_train, y_train)
    return encoder, imp, Xstd, Xnorm, ystd


def train_model(df_train, y_train):
    model = HuberRegressor(alpha=0.001, epsilon=1.35, max_iter=1000).fit(df_train, y_train)
    return model


def calc_results(model, df_train, y_train, df_test, y_test, ystd):
    model_name = type(model).__name__

    # Prediction of train values (standardized):
    y_pred_train_std = model.predict(df_train)
    mse_train_std = mean_squared_error(y_train, y_pred_train_std)
    mse_train_std = round(mse_train_std, 4)
    
    # Prediction of test values (standardized):
    y_pred_test_std = model.predict(df_test)
    mse_test_std = mean_squared_error(y_test, y_pred_test_std)
    mse_test_std = round(mse_test_std, 4)
    
    # De-standardize the predicted values and actual test values:
    # Train:
    y_pred_train_true = ystd.inverse_transform(y_pred_train_std.reshape(-1, 1)).ravel()
    y_train_true = ystd.inverse_transform(y_train.reshape(-1, 1)).ravel()
    rmse_train = root_mean_squared_error(y_train_true, y_pred_train_true)
    rmse_train = round(rmse_train, 2)
    # Test:
    y_pred_test_true = ystd.inverse_transform(y_pred_test_std.reshape(-1, 1)).ravel()
    y_test_true = ystd.inverse_transform(y_test.reshape(-1, 1)).ravel()
    rmse_test = root_mean_squared_error(y_test_true, y_pred_test_true)
    rmse_test = round(rmse_test, 2)
    
    scores = [[model_name, mse_train_std, mse_test_std, rmse_train, rmse_test]]
    df_scores = pd.DataFrame(scores, columns=['model', 'MSE_train_std', 'MSE_test_std', 'RMSE_train', 'RMSE_test'])
    return df_scores


def save_models(output_file, encoder, imp, Xstd, Xnorm, ystd, model):    
    with open(output_file, 'wb') as f_out:
        pickle.dump((encoder, imp, Xstd, Xnorm, ystd, model), f_out)


def complete_train_workflow(input_file, output_file):
    dataset = load_dataset(input_file)
    df_train, y_train, df_test, y_test = split_dataset(dataset, years_for_test=3)

    encoder, imp, Xstd, Xnorm, ystd = train_preprocessing_workflow(df_train, y_train)
    df_train = data_preprocessing_workflow(df_train, encoder, imp, Xstd, Xnorm)
    y_train = ystd.transform(y_train.to_numpy().reshape(-1, 1)).ravel()

    model = train_model(df_train, y_train)
    save_models(output_file, encoder, imp, Xstd, Xnorm, ystd, model)

    results = calc_results(model, df_train, y_train, df_test, y_test, ystd)
    print(f"MODEL RESULTS:\n{results}")


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description='''Pipeline to train the Life Expectancy Prediction model''')
    
    parser.add_argument('-i', action='store', help='Path to the input dataset', dest='INPUT',
                        required=False, default='data/raw/life_expectancy_data.csv')
    parser.add_argument('-o', action='store', help='Path to output the models', dest='OUTPUT',
                        required=False, default='app/life_expectancy_prediction_models.bin')
    args = parser.parse_args()
    input_file = args.INPUT
    output_file = args.OUTPUT

    complete_train_workflow(input_file, output_file)


if __name__ == '__main__':  
    main()
