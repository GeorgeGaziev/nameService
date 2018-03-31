from flask import request, jsonify, render_template
from app import app
from app.forms import InputForm
from app import Inductor

@app.route('/')
@app.route('/index')
def index():
    form = InputForm()
    return render_template('index.html', title='Обработка ФИО', form=form)

@app.route('/process', methods=['GET', 'POST'])
def process():
    if request.method == 'POST':
        print (type(request.data))
        print (type(request.form))
        print ("--request.form--")
        for i in request.form:
            print(i)
        print ("----")
        print ("--request.get_json()--")
        content = request.get_json(silent=True)
        print (content)
        print ("----")
        #inputText = str(request.get_json())
        #print ("inputText: " + inputText)

        inputText = str((request.data))
        print (inputText)
        #print ("\nrequest.get_json(): ")
        #print (request.get_json())
        #print ("\nrequest.get_json(request.data):")
        #print (request.get_json(request.data))
        outputText = Inductor.ProcessSingle(inputText)
        print ("\noutputText: " + outputText)
        data = {'outputText': outputText}
        data = jsonify(data)
        return data
    #return render_template('react-material/index.html')
