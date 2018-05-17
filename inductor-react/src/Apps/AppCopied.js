import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { withStyles } from 'material-ui/styles';
//import Button from 'material-ui/Button';
import Card, { CardActions, CardContent, CardMedia } from 'material-ui/Card';
import TextField from 'material-ui/TextField';
import Typography from 'material-ui/Typography';
//import Table, { TableBody, TableCell, TableHead, TableRow } from 'material-ui/Table';
//import Paper from 'material-ui/Paper';
import $ from 'jquery';

import {
  SortingState, EditingState, PagingState,
  IntegratedPaging, IntegratedSorting,
} from '@devexpress/dx-react-grid';
import {
  Grid,
  Table, TableHeaderRow, TableEditRow, TableEditColumn,
  PagingPanel, DragDropProvider, TableColumnReordering,
} from '@devexpress/dx-react-grid-material-ui';
import Paper from 'material-ui/Paper';
import Dialog, {
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from 'material-ui/Dialog';
import Button from 'material-ui/Button';
import IconButton from 'material-ui/IconButton';
import Input from 'material-ui/Input';
import Select from 'material-ui/Select';
import { MenuItem } from 'material-ui/Menu';
//import { TableCell } from 'material-ui/Table';

import DeleteIcon from 'material-ui-icons/Delete';
import EditIcon from 'material-ui-icons/Edit';
import SaveIcon from 'material-ui-icons/Save';
import CancelIcon from 'material-ui-icons/Cancel';
//import { withStyles } from 'material-ui/styles';



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
    dialog: {
		width: 'calc(100% - 16px)',
	},
	inputRoot: {
		width: '100%',
	},
});

const AddButton = ({ onExecute }) => (
  <div style={{ textAlign: 'center' }}>
    <Button
      color="primary"
      onClick={onExecute}
      title="Create new row"
    >
      New
    </Button>
  </div>
);

const EditButton = ({ onExecute }) => (
  <IconButton onClick={onExecute} title="Edit row">
    <EditIcon />
  </IconButton>
);

const DeleteButton = ({ onExecute }) => (
  <IconButton onClick={onExecute} title="Delete row">
    <DeleteIcon />
  </IconButton>
);

const CommitButton = ({ onExecute }) => (
  <IconButton onClick={onExecute} title="Save changes">
    <SaveIcon />
  </IconButton>
);

const CancelButton = ({ onExecute }) => (
  <IconButton color="secondary" onClick={onExecute} title="Cancel changes">
    <CancelIcon />
  </IconButton>
);

const commandComponents = {
  add: AddButton,
  edit: EditButton,
  delete: DeleteButton,
  commit: CommitButton,
  cancel: CancelButton,
};

const Command = ({ id, onExecute }) => {
  const CommandButton = commandComponents[id];
  return (
    <CommandButton
      onExecute={onExecute}
    />
  );
};

const Cell = (props) => {
  return <Table.Cell {...props} />;
};

const EditCell = (props) => {
  return <TableEditRow.Cell {...props} />;
};

const getRowId = row => row.id;


class App extends Component {


    createData (name,mistake) {
        id += 1;
        return { id, name, mistake};
    }

    items : [
        createData('Иванов Иван Иванович', 'Ошибка была'),
        createData('Семенов Семен Семенович', ''),
        createData('Ирина Алексеевна Ющикова', '')
    ];

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
                console.log(resultArray);
                items.push(createData(result));
                console.log(items);
                $('#outputText').val(data['outputText']);
            }
        });
        console.log("result from page: " + result);
    }

	constructor(props) {
    super(props);

    this.state = {
      columns: [
        { name: 'name', title: 'ФИО' },
        { name: 'mistake', title: 'Ошибки' },
      ],
      rows: items,
      sorting: [],
      editingRowIds: [],
      addedRows: [],
      rowChanges: {},
      //currentPage: 0,
      deletingRows: [],
      //pageSize: 0,
      //pageSizes: [5, 10, 0],
      columnOrder: ['name', 'mistake'],
    };

    this.changeSorting = sorting => this.setState({ sorting });
    this.changeEditingRowIds = editingRowIds => this.setState({ editingRowIds });
    this.changeAddedRows = addedRows => this.setState({
      addedRows: addedRows.map(row => (Object.keys(row).length ? row : {
        name: "",
        mistake: "",
      })),
    });
    this.changeRowChanges = rowChanges => this.setState({ rowChanges });
    this.changeCurrentPage = currentPage => this.setState({ currentPage });
    this.changePageSize = pageSize => this.setState({ pageSize });
    this.commitChanges = ({ added, changed, deleted }) => {
      let { rows } = this.state;
      // if (added) {
      //   const startingAddedId = (rows.length - 1) > 0 ? rows[rows.length - 1].id + 1 : 0;
      //   rows = [
      //     ...rows,
      //     ...added.map((row, index) => ({
      //       id: startingAddedId + index,
      //       ...row,
      //     })),
      //   ];
      // }
      // if (changed) {
      //   rows = rows.map(row => (changed[row.id] ? { ...row, ...changed[row.id] } : row));
      // }
      this.setState({ rows, deletingRows: deleted || this.state.deletingRows });
    };
    this.cancelDelete = () => this.setState({ deletingRows: [] });
    this.deleteRows = () => {
      const rows = this.state.rows.slice();
      this.state.deletingRows.forEach((rowId) => {
        const index = rows.findIndex(row => row.id === rowId);
        if (index > -1) {
          rows.splice(index, 1);
        }
      });
      this.setState({ rows, deletingRows: [] });
    };
    this.changeColumnOrder = (order) => {
      this.setState({ columnOrder: order });
    };
  }
	
    render() {
		
	const { classes } = this.props;
	
    const {
      rows,
      columns,
      tableColumnExtensions,
      sorting,
      editingRowIds,
      addedRows,
      rowChanges,
      currentPage,
      deletingRows,
      pageSize,
      pageSizes,
      columnOrder,
      currencyColumns,
      percentColumns,
    } = this.state;

    return (
      <div id="form">	  
	  <Paper className={classes.root}>
	  		<Typography variant="headline" component="h3"> Сервис по исправлению ФИО</Typography>
			<Typography component="p">
			<TextField
				id="inputText"
				margin="normal"
				multiline
				rowsMax="15"
				label={"Ввод"}
				className={classes.textField}
			/>
			</Typography>
			<Typography component="p" className={classes.typography}>
			<Button
				onClick={this.processInput}
				id="launch"
				variant="raised">
				Надпись
			</Button>
			</Typography>
	  <Grid
          rows={rows}
          columns={columns}
          getRowId={getRowId}
        >
          <SortingState
            sorting={sorting}
            onSortingChange={this.changeSorting}
          />
          <PagingState
            currentPage={currentPage}
            onCurrentPageChange={this.changeCurrentPage}
            pageSize={pageSize}
            onPageSizeChange={this.changePageSize}
          />

          <IntegratedSorting />
          <IntegratedPaging />

          <EditingState
            editingRowIds={editingRowIds}
            onEditingRowIdsChange={this.changeEditingRowIds}
            rowChanges={rowChanges}
            onRowChangesChange={this.changeRowChanges}
            addedRows={addedRows}
            onAddedRowsChange={this.changeAddedRows}
            onCommitChanges={this.commitChanges}
          />

          <DragDropProvider />

          <Table
            columnExtensions={tableColumnExtensions}
            cellComponent={Cell}
          />

          <TableColumnReordering
            order={columnOrder}
            onOrderChange={this.changeColumnOrder}
          />

          <TableHeaderRow showSortingControls />
          <TableEditRow
            cellComponent={EditCell}
          />
          <TableEditColumn
            width={120}
            showAddCommand={!addedRows.length}
            showEditCommand
            showDeleteCommand
            commandComponent={Command}
          />
          <PagingPanel
            pageSizes={pageSizes}
          />
        </Grid>

        <Dialog
          open={!!deletingRows.length}
          onClose={this.cancelDelete}
          classes={{ paper: classes.dialog }}
        >
          <DialogTitle>Delete Row</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Are you sure to delete the following row?
            </DialogContentText>
            <Paper>
              <Grid
                rows={rows.filter(row => deletingRows.indexOf(row.id) > -1)}
                columns={columns}
              >
                <Table
                  columnExtensions={tableColumnExtensions}
                  cellComponent={Cell}
                />
                <TableHeaderRow />
              </Grid>
            </Paper>
          </DialogContent>
          <DialogActions>
            <Button onClick={this.cancelDelete} color="primary">Cancel</Button>
            <Button onClick={this.deleteRows} color="secondary">Delete</Button>
          </DialogActions>
        </Dialog>
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
