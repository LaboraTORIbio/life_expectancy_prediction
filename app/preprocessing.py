import pickle
import pandas as pd
import numpy as np


def load_models():
    model_file = 'app/life_expectancy_prediction_models.bin'
    with open(model_file, 'rb') as f_in:
        encoder, imp, Xstd, Xnorm, ystd, model = pickle.load(f_in)
    return encoder, imp, Xstd, Xnorm, ystd, model


def feature_selection(df):
    cols_to_keep = ['year', 'status', 'adult_mortality', 'infant_mortality_rate',
                    'gdp', 'total_expenditure', 'income_composition_of_resources',
                    'polio', 'diphtheria', 'hiv_aids', 'thinness_5-9_years', 'thinness_10-19_years',
                    'alcohol', 'schooling']
    df_keep = df.loc[:, cols_to_keep]
    return df_keep


def onehot_encode(df, encoder):
    status_encoded = encoder.transform(df['status'].to_numpy().reshape(-1, 1))
    encoded_df = pd.DataFrame(status_encoded, columns=encoder.get_feature_names_out(['status']))
    df_encoded = pd.concat([df.drop('status', axis=1), encoded_df], axis=1)
    return df_encoded


def data_imputation(df, imp):
    df['income_composition_of_resources'] = df['income_composition_of_resources'].replace(0, np.nan)
    imp_df = imp.transform(df)
    df.loc[:, :] = imp_df
    return df


def data_scaling(df, Xstd, Xnorm):
    cols_standard = ['gdp', 'total_expenditure', 'alcohol', 'schooling']
    cols_minmax = ['adult_mortality', 'infant_mortality_rate', 'polio', 'diphtheria', 'hiv_aids',
                   'thinness_5-9_years', 'thinness_10-19_years']
    df[cols_standard] = Xstd.transform(df[cols_standard])
    df[cols_minmax] = Xnorm.transform(df[cols_minmax])
    return df


def preprocess(data):
    df = pd.DataFrame([data])
    df_keep = feature_selection(df)
    encoder, imp, Xstd, Xnorm, *_ = load_models()
    df_encoded = onehot_encode(df_keep, encoder)
    df_imp = data_imputation(df_encoded, imp)
    df_scaled = data_scaling(df_imp, Xstd, Xnorm)
    df_processed = df_scaled.drop('year', axis=1)
    return df_processed
