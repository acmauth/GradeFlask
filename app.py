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


def predict(student_id, courses):
    # Get the data from the POST request.
    student = models.get_user(app.config["MONGO_DB_URL"].replace("<password>", app.config["MONGO_DB_PASSWORD"]),
                              student_id)
    if student is not None:
        student_df = pd.DataFrame.from_dict([student], orient="columns")
        predictions = dict()
        for course in courses:
            if course in models.available_courses(app.config["ML_MODELS_FOLDER"]):
                ml_model = ml_models[course]
                features = ml_model.get_booster().feature_names
                selected_features = student_df[features]
                predictions[course] = str(ml_model.predict(selected_features)[0])
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
    app.run(port=app.config["PORT"], debug=app.config["DEBUG"])
