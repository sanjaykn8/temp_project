from flask import Flask, render_template, request
import pandas as pd
import joblib
import numpy as np

app = Flask(__name__)

# Load the trained model and encoders
model = joblib.load("final_model.pkl")
scaler = joblib.load("scaler.pkl")  # Load fitted MinMaxScaler
encoder_education = joblib.load("encoder_education.pkl")  # LabelEncoder for Education Level
encoder_course = joblib.load("encoder_course.pkl")  # LabelEncoder for Course Name

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None

    if request.method == "POST":
        try:
            # Get form data
            age = int(request.form["age"])
            education_level = request.form["education_level"]
            course_name = request.form["course_name"]
            time_spent = float(request.form["time_spent"])
            quiz_score = float(request.form["quiz_score"])
            final_exam_score = float(request.form["final_exam_score"])

            # Encode categorical variables (use the same encoder from training)
            education_level_encoded = encoder_education.transform([education_level])[0]
            course_name_encoded = encoder_course.transform([course_name])[0]

            # Scale time spent (use the already fitted MinMaxScaler)
            scaled_time_spent = scaler.transform(np.array([[time_spent]]))[0][0]

            # Compute efficiency score (matching training logic)
            efficiency_score = (0.4 * final_exam_score) + (0.4 * quiz_score) + (0.2 * scaled_time_spent * 100)

            # Create DataFrame for model input
            input_data = pd.DataFrame([[age, education_level_encoded, course_name_encoded, time_spent, quiz_score, final_exam_score]],
                                      columns=['Age', 'Education_Level', 'Course_Name', 'Time_Spent_on_Videos', 'Quiz_Scores', 'Final_Exam_Score'])

            # Predict proficiency level
            prediction_encoded = model.predict(input_data)[0]

            # Convert prediction back to category (beginner, intermediate, advanced)
            proficiency_labels = ["beginner", "intermediate", "advanced"]
            prediction = proficiency_labels[prediction_encoded]

        except Exception as e:
            prediction = f"Error: {e}"

    return render_template("index.html", prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)
