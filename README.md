# Grade++ Flask #

## Info ##
This is an API for predicting the student's grades. It is meant to be used alongside with
[GradeServer](https://github.com/acmauth/GradeServer). Given a request with the student's ID and the courses to 
be predicted it returns the predicted courses for each of the courses along with the version of the model. The information of the student are retrieved from
a MongoDB. 

A sample json request: 

```json
{
  "id": "student_id", 
  "courses": ["NCO-04-05", "NCO-05-06"]
}
```

And the sample response:
```json
{
    "version": "1",
    "NCO-04-05": "9.996448",
    "NCO-05-06": "Not Available"
}
```

## How it works ##
This is a simple Flask application. You can run the application by executing the following:
```python
python app.py
```
The packages needed for the app to run are in **requirements.txt** file. You can configure the app by using copying the 
**config_default.py** file as **config.py**. In this file you can specify the Mongo URL and Mongo Password. 

