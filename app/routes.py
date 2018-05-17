# coding=utf-8
from flask import request, jsonify, render_template
from app import app
from app.forms import InputForm
from app import Inductor
from app import utils

@app.route('/')
@app.route('/index')
def index():
    form = InputForm()
    return render_template('index.html', title='Обработка ФИО', form=form)

@app.route('/process', methods=['GET', 'POST'])
def process():
    if request.method == 'POST':
        inputData = request.form['inputData']
        inputData = inputData.splitlines()
        inputArray = []
        for i in inputData:
            inputArray.append(i)
        outputText = Inductor.NotBruteAtAll(inputArray)
        outputString = ""
        result = outputText
        for res in outputText:
            outputString += res[0][0] +'|'
        return jsonify({'outputText': outputString, 'outputArray':result})
