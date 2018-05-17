import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { withStyles } from 'material-ui/styles';
import Button from 'material-ui/Button';
import TextField from 'material-ui/TextField';
import Typography from 'material-ui/Typography';
import Table, { TableBody, TableCell, TableHead, TableRow } from 'material-ui/Table';
import Paper from 'material-ui/Paper';
import $ from 'jquery';

let id = 0;
function createData(name,mistake) {
  id += 1;
  return { id, name, mistake};
}

const styles = theme => ({
	root: theme.mixins.gutters({
		paddingTop: 16,
		paddingBottom: 16,
		marginTop: theme.spacing.unit * 3, 
	}),
	button: {
		margin: theme.spacing.unit,
	},
    table: {
		minWidth: 700,
	},
	textField: {
		marginLeft: theme.spacing.unit,
		marginRight: theme.spacing.unit,
		width: 500,
	},
	typography: {
		marginTop: 20,
		marginBottom: 20,
	},
});
let result;
let splited=[];

class App extends Component {

    constructor(){
        super();
        this.state = {
            items : [],
			mistakes : []
        };
        this.processInput = this.processInput.bind(this);
    };

    processInput(e){
        let inputText = $('#inputText').val();
        $.ajax({
            url: 'http://127.0.0.1:5000/process',
            data: {'inputData': inputText},
            method: 'POST',
            success: function(data) {
                result = data['outputText'];
                splited = result.split("|");
                splited.splice(-1,1);
            },
            async: false
        });
        let newItems=[];
        splited.forEach(function(element) {
            newItems.push(createData(element));
        });
        this.setState({items : newItems.slice()});
    }

    render() {
	    const { classes } = this.props;
        return (
        	<div id="form">
	    		<Paper className={classes.root}>
					<div align="center">
	    				<Typography variant="headline" component="h3">Сервис по исправлению ФИО</Typography>
	    				<Typography component="p">
	    				<TextField
	    					id="inputText"
	    					margin="normal"
	    					multiline
	    					label={"Ввод"}
	    					className={classes.textField}
	    				/>
	    				</Typography>
	    				<Typography component="p" className={classes.typography}>
	    				<Button
                    	    onClick={ () => {
                    	        this.processInput();
                    	    }}
                    	    id="launch"
	    					variant="raised">
	    					Обработать!
	    				</Button>
	    				</Typography>
                    </div>
	    		<Table className={classes.table}>
	    			<TableHead>
	    			 	 <TableRow>
	    					 <TableCell>ФИО</TableCell>
	    				 </TableRow>
	    			</TableHead>
	    			<TableBody>
	    		   	{this.state.items.map(n => {
	    			return (
	    			 	<TableRow key={n.id}>
	    					<TableCell>{n.name}</TableCell>
	    			    </TableRow>
	    			    );
	    		   	    })
	    		   	}
	    			</TableBody>
	    		</Table>
	    	</Paper>
          </div>
        );
  }
}
//npx webpack --config webpack.config.js

App.propTypes = {
  classes: PropTypes.object.isRequired,
};
export default withStyles(styles)(App);
