from flask import Flask, request, jsonify
from app.preprocessing import preprocess
from app.model import predict_life_expec


app = Flask('life_expectancy')


@app.route('/predict', methods=['POST'])
def predict():
    country_data = request.get_json()

    country_data_processed = preprocess(country_data)
    life_expectancy_pred = predict_life_expec(country_data_processed)
    
    result = {
        'life_expectancy': float(life_expectancy_pred)
    }

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9696)
