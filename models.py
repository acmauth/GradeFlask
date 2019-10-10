import os
import pickle

import pymongo


def read_all_ml_models(models_folder):
    ml_models = dict()
    for file in os.listdir(models_folder):
        if file.endswith('.dat'):
            model = pickle.load(open(models_folder + file, 'rb'))
            ml_models[file.replace(".dat", "")] = model
    return ml_models


def get_user(mongo_db, user_id):
    client = pymongo.MongoClient(mongo_db)
    db = client.students
    grades = db.gradeplus
    students = grades.find({"student_id": user_id})
    if students.count() > 0:
        return students[0]
    else:
        return None


def available_courses(models_folder):
    available_models = []
    for file in os.listdir(models_folder):
        if file.endswith('.dat'):
            available_models.append(file.replace(".dat", ""))
    return available_models
