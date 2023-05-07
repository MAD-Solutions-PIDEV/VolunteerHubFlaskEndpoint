import requests
import torch as torch
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from flask import Flask
from organizationClassification import organizations_classification
from sentimentAnalysis import sentiment_analysis
from donationPrediction import predict_donation
from flask import request
app = Flask(__name__)


@app.route('/predict/classifyOrgs')
def launch_orgs_classification():
    organizations_classification()
    return ''


@app.route('/predict/classifyEvents')
def launch_sentiment_analysis():
    sentiment_analysis()
    return ''


@app.route('/predict/donation', methods=["POST"])
def launch_donation_prediction():
    data = request.json
    #  Data recperation
    donors = pd.read_csv('donationData.csv')

    # Data Preparation
    X = donors[['age', 'gender', 'donation_times', 'donation_reason']]
    y = donors['donation_amount']

    # data transformation

    X = pd.get_dummies(X, columns=['gender', 'donation_reason'])
    X.dropna(inplace=True)
    y = y[X.index]

    # data normalization
    scaler = StandardScaler()
    X = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)

    # Model Creation and training
    model = LinearRegression()
    model.fit(X, y)
    predict_donation(data)


if __name__ == '__main__':
    app.run()
