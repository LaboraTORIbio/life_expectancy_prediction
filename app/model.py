import pickle


def load_models():
    model_file = 'app/life_expectancy_prediction_models.bin'
    with open(model_file, 'rb') as f_in:
        encoder, imp, Xstd, Xnorm, ystd, model = pickle.load(f_in)
    return encoder, imp, Xstd, Xnorm, ystd, model


def predict_transform(df, model, ystd):
    y_pred = model.predict(df)
    y_pred_true = ystd.inverse_transform(y_pred.reshape(-1, 1)).ravel()
    return y_pred_true


def predict_life_expec(df):
    *_, ystd, model = load_models()
    life_expectancy = predict_transform(df, model, ystd).round(2)
    return life_expectancy
