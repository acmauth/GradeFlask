# Import libraries

import json

import pandas as pd
from bson import ObjectId
from flask import Flask, request, jsonify, render_template

import models

app = Flask(__name__, instance_relative_config=True)
# Load the default configuration
app.config.from_object('config')

# Load the model
ml_models = models.read_all_ml_models(app.config["ML_MODELS_FOLDER"])


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.get_json(force=True)
        if "id" in data:
            student_id = data["id"]
        else:
            return {"Error": "Please provide a student ID (id)."}
        if "courses" in data:
            courses = data["courses"]
        else:
            return {"Error": "Please provide course IDs in a list (courses)."}
        return predict(student_id, courses)
    else:
        return render_template("index.html")


@app.route("/courses", methods=['GET'])
def get_courses():
    return jsonify(models.available_courses(app.config["ML_MODELS_FOLDER"]))


@app.route("/check_version", methods=['GET'])
def get_version():
    return jsonify(app.config["VERSION"])


def predict(student_id, courses):
    # Get the data from the POST request.
    student = models.get_user(app.config["MONGO_DB_URL"].replace("<password>", app.config["MONGO_DB_PASSWORD"]),
                              student_id)
    if student is not None:
        if 'grades' in student:
            student_df = pd.DataFrame(student['grades'])
            student_df = student_df[['_id', 'grade']]
            student_df_transposed = student_df.T
            headers = student_df_transposed.iloc[0]
            student_grades = pd.DataFrame(student_df_transposed.values[1:], columns=headers)
            predictions = dict()
            predictions["version"] = app.config["VERSION"]
            for course in courses:
                if course in models.available_courses(app.config["ML_MODELS_FOLDER"]):
                    ml_model = ml_models[course]
                    features = ml_model.get_booster().feature_names
                    selected_features = dict()
                    courses_with_grade = student_grades.columns
                    for feature in features:
                        if feature in courses_with_grade:
                            selected_features[feature] = student_grades[feature].values[0]
                        else:
                            selected_features[feature] = -1
                    selected_features = pd.DataFrame(selected_features, index=[1, ])
                    prediction = round(ml_model.predict(selected_features)[0],2)
                    if prediction > 10:
                        prediction = 10.00
                    predictions[course] = str(prediction)
                else:
                    predictions[course] = "Not Available"
            return JSONEncoder().encode(predictions)
    else:
        return {"Error": "Student not found"}


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


if __name__ == '__main__':
    app.run()
