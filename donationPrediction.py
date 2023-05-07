import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import json
import sys

#  Data recperation
donors = pd.read_csv('donationData.csv')

# Data Preparation
X = donors[['age', 'gender', 'donation_times','donation_reason']]
y = donors['donation_amount']

# data transformation

X = pd.get_dummies(X, columns=['gender','donation_reason'])
X.dropna(inplace=True)
y = y[X.index]


#data normalization
scaler = StandardScaler()
X = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)


# Model Creation and training
model = LinearRegression()
model.fit(X, y)

def predict_donation(new_donor):
    new_donor = pd.DataFrame([new_donor], columns=['age', 'gender', 'donation_times', 'donation_reason'])
    new_donor = pd.get_dummies(new_donor, columns=['gender','donation_reason'])
    new_donor = new_donor.reindex(columns=X.columns, fill_value=0)  # Ajouter les colonnes manquantes
    new_donor = scaler.transform(new_donor)

    new_donor = pd.DataFrame(new_donor, columns=X.columns)

    prediction = model.predict(new_donor)

    return prediction[0]

if __name__ == '__main__':
    # get JSON Data
    if len(sys.argv) > 1:
        new_donor = json.loads(sys.argv[1])
    else:
        new_donor = {}
    prediction = predict_donation(new_donor)
    print(prediction)
