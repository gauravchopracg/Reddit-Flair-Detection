from flask import render_template, request, jsonify
from app import app
from utils import *
from app.forms import RedditForm
from werkzeug.utils import secure_filename
import os


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = RedditForm()
    if form.validate_on_submit():
        path = form.url.data
        path = [path]
        res, flair = process(list(path))
        predicted_flair=res[path[0]]#str(a[0])
        actual_flair = flair#b#predict(url)
        return render_template('login.html',  title=predicted_flair, form=form, actual_flair=actual_flair, predicted_flair=predicted_flair)
    return render_template('login.html',  title='FindFlair', form=form)

# automated testing endpoint
# this endpoint will be used for testing performance of the classifier
@app.route('/automated_testing', methods=['GET', 'POST'])
def test():
    json = {}
    if request.method == 'POST':
        for i in request.files:
            file = request.files[i]
            urls = file.read()
            urls = urls.decode("utf-8").split("\n")
            urls = [i.replace("\r","") for i in urls]
            res = process(urls)
            json = res[0]
            return jsonify(json)
    return "Error in file upload"