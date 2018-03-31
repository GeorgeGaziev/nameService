import React, { Component } from 'react';
import Button from 'material-ui/Button'
import Card from 'material-ui/Card'
import TextField from 'material-ui/TextField'
import $ from 'jquery';


class App extends Component {
     processInput(e){
        //var city = $(e.currentTarget).data('city');
        var inputText = $('#inputText').val();
        console.log("inputText from page: " + inputText);
        $.ajax({
            url: 'http://127.0.0.1:5000/process',
            data: {'inputText': encodeURIComponent(inputText)},
            method: 'POST',
            contentType: 'application/json;charset=windows-1251',
            success: function(data) {
                console.log(data);
                $('#inputText').val('');
                $('#outputText').val(data['outputText']);
                //$('#process').html('Результат обработки: ' + data['outputText'])
            }
        });
    }

    render() {
    return (
      <div id="form">
            <TextField
                id="inputText"
                margin="normal"
                multiline
                rowsMax="4"
                defaultValue={"Работает само по себе"}
                label={"Ввод"}
            >
            </TextField>
            <Button
                onClick={this.processInput}
                id="launch"
                variant="raised">
                Надпись
            </Button>
          <TextField
              id="outputText"
              margin="normal"
              multiline
              rowsMax="4"
              defaultValue={"Работает само по себе"}
              label={"Вывод"}
          >
          </TextField>
      </div>

    );
  }
}

//npx webpack --config webpack.config.js

export default App;
