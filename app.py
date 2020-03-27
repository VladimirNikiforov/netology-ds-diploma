import pandas as pd
from flask import Flask, jsonify, request
import pickle

# load model
model = pickle.load(open('model.pkl','rb'))

# app
app = Flask(__name__)

# routes
@app.route('/', methods=['POST'])

def predict():
    def check_alert(y_predicted):
        # Return the most important (heaviest by weight) flag as a result
        '''
        Rules:
            If percent is more than first level (50% for example) we need ALERT (weight=1) because it's suspicious transaction.
            If percent is more than second level (75% for example) we need LOCK and ALERT (weight=2) because it's very suspicious transaction and it's better to lock user and send alert signal to work with this user.
            If percent is more than max level (90% for example) we need LOCK (weight=3) because it's fraudster.
        '''

        # dictionary of alerts
        dict_of_alerts = {0: ['PASS'],
                          1: ['ALERT_AGENT'],
                          2: ['LOCK_USER', 'ALERT_AGENT'],
                          3: ['LOCK_USER']
                          }
        # for each prediction in y_prediction check the rules, get the max weight and apply dictionary to get the alert
        return dict_of_alerts[max([{y >= .9: 3,
                                    .75 <= y < .9: 2,
                                    .5 <= y < .75: 1,
                                    y < .5: 0}[True] for y in y_predicted])]

    # get data
    data = request.get_json(force=True)

    # convert data into dataframe
    data_df = pd.DataFrame.from_dict(data)

    # predictions
    result = model.predict_proba(data_df)[:, 1]

    # send back to browser
    output = {'ACTION': check_alert(result)}

    # return data
    return jsonify(results=output)

if __name__ == '__main__':
    app.run(port = 7441, debug=True)