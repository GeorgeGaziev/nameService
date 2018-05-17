import React, { Component } from 'react';
import Button from 'material-ui/Button';
import Card from 'material-ui/Card';
import TextField from 'material-ui/TextField';
import PropTypes from 'prop-types';
import { withStyles } from 'material-ui/styles';
import Paper from 'material-ui/Paper';
import Typography from 'material-ui/Typography';
import $ from 'jquery';


class App extends Component {

    processInput(e){
        let inputText = $('#inputText').val();
        let result;
        let resultArray;
        console.log("inputText from page: " + inputText);
        $.ajax({
            url: 'http://127.0.0.1:5000/process',
            data: {'inputData': inputText},
            method: 'POST',
            success: function(data) {
                result = data['outputText'];
                console.log(result);
                resultArray = data['outputArray'];
                this.forceUpdate().bind(this);
                console.log(resultArray);
                $('#outputText').val(data['outputText']);
            }
        });
        console.log("result from page: " + result);
    }

    setOutputData(outputArray){

    }

    render() {
        return (
            <div>
                <div>
                    <Paper
                        style={{marginRight: 20}}
                        elevation={4}>
                            <div id="form">
                                <TextField
                                    id="inputText"
                                    margin="normal"
                                    multiline
                                    defaultValue={"Иванов Иван \n Петров Пётр"}
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
                                    label={"Вывод"}
                                >
                                </TextField>
                            </div>
                    </Paper>
                </div>
            </div>
        );
    }
}

//npx webpack --config webpack.config.js

export default App;
