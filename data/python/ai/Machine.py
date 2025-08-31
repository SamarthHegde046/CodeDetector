from sklearn.linear_model import LinearRegression
import numpy as np

# Training data
X = np.array([[1], [2], [3], [4]])
y = np.array([2, 4, 6, 8])

# Model
model = LinearRegression()
model.fit(X, y)

# Prediction
print(model.predict([[5]]))  # Output: [10.]