# -----------------------------------------------------------------------------
# FILE NAME:         aalarconbojorquez_pa.py
# USAGE:             python3 aalarconbojorquez_pa.py < PA2_test.sql
# NOTES:             Runs using the standards file input {filename} < PA2_test.sql
#                    or line by line input python3 aalarconbojorquez_pa.py
#
# MODIFICATION HISTORY:
# Author             Date           Modification(s)
# ----------------   -----------    ---------------
# Andy Alarcon       2020-09-27     1.0 ... Added multipleline command parsing, Insertion command with type checking
# Andy Alarcon       2020-09-28     1.1 ... Added column specific select command
# -----------------------------------------------------------------------------

import sys
import re
import os
import shutil

# Global variable to keep track of the current DB in use
GlobalCurrentDirectory = ""

# A class to handle the metadata manipulation
class MetaData(object):
    pass

#Operators for defined for conditon checking
op = {'>': lambda x, y: x > y,
      '<': lambda x, y: x < y,
      '>=': lambda x, y: x >= y,
      '<=': lambda x, y: x <= y,
      '==': lambda x, y: x == y,
      '!=': lambda x, y: x != y,}


def main():

    # List that holds all commands that will executed
    CommandsList = []
    StandardInputisActive = False

    # There is NOT standard input file attached
    if sys.stdin.isatty():

        try:
            LineInputCommand = str(input("--> "))
        except:
            print("Invalid Input Please Try again")

        CommandsList.append(LineInputCommand)

    # There is a standard input file attached
    else:
        # Returns a list of commands to execute
        CommandsList = ReadCommandsFileInput()
        StandardInputisActive = True

    # With the full CommandsList Process the first command and then delete the first one after it is done
    # Standard input
    if StandardInputisActive:
        while CommandsList[0].lower() != ".exit":
            ExecuteCommand(CommandsList[0])
            CommandsList.pop(0)

    # Line by Line input with multiple line queries
    else:
        while LineInputCommand.lower() != ".exit":
            if LineInputCommand.endswith(';'):
                LineInputCommand = LineInputCommand.replace('\t', '')
                ExecuteCommand(LineInputCommand)
                LineInputCommand = ''
            while not LineInputCommand.endswith(';'):
                tempInput = str(input("--> "))
                if tempInput.lower() == '.exit':
                    LineInputCommand = '.exit'
                    break
                else:
                    LineInputCommand = LineInputCommand + ' ' + tempInput

    print("All done.")


# ----------------------------------------------------------------------------
# FUNCTION NAME:     ExecuteCommand(str)
# PURPOSE:           This function reads a single command, parses it and executes
#                    the command
# -----------------------------------------------------------------------------


def ExecuteCommand(commandLine):

    unalteredCommandLine = commandLine

    # Error message that is displayed when a command line has an
    # invalid number of arguments
    argumentErrorMessage = "!Failed a syntax error occured"

    # Parse the single command and returns a list
    commandLine = ParseCommandByWord(commandLine)

    # Use each parsed keyword and execute the corresponding command
    if not commandLine:
        print('', end='')
    else:

        # If the first keyword is create
        if commandLine[0].lower() == "create":

            # Check the remaining ones and execute or display an error if invalid
            try:
                if commandLine[1].lower() == "database":
                    CreateDatabase(commandLine[2])
                elif commandLine[1].lower() == "table":
                    CreateTable(commandLine[2], unalteredCommandLine)
                else:
                    print("!Failed CREATE command argumments not recognized")
            except:
                print(argumentErrorMessage)

        # If the first keyword is drop
        elif commandLine[0].lower() == "drop":

            # Check the remaining ones and execute or display an error
            try:
                if commandLine[1].lower() == "database":
                    DropDatabase(commandLine[2])
                elif commandLine[1].lower() == "table":
                    DropTable(commandLine[2])
                else:
                    print("!Failed DROP command argumments not recognized")

            except:
                print(argumentErrorMessage)

        # If the first keyword is alter
        elif commandLine[0].lower() == "alter":
            # Check the remaining ones and execute or display an error
            try:
                if commandLine[1].lower() == "table":
                    AlterTable(unalteredCommandLine, commandLine[2:])
                else:
                    print("!Failed ALTER command argumments not recognized")

            except:
                print(argumentErrorMessage)

        # If the first keyword is use
        elif commandLine[0].lower() == "use":
            # Check the remaining ones and execute or display an error
            try:
                UseDatabase(commandLine[1])
            except:
                print(argumentErrorMessage)

        # If the first keyword is select
        elif commandLine[0].lower() == "select":
            # Check the remaining ones and execute or display an error
            try:
                SelectCommand(commandLine[0:])
            except:
                print(argumentErrorMessage)

        # IF the first keyword is insert
        elif commandLine[0].lower() == "insert":
            # Check the remaining ones and execute or display an error
            try:
                if commandLine[1].lower() == "into":
                    InsertCommand(unalteredCommandLine, commandLine[2:])
                else:
                    print("!Failed INSERT command argumments not recognized")
            except:
                print(argumentErrorMessage)

        # If the first keyword was not recognized above display an error
        else:
            print("!Failed command : '" + commandLine[0] + "' not recognized")

# ----------------------------------------------------------------------------
# FUNCTION NAME:     GenerateMetadataObject(str)
# PURPOSE:           This function creates a object based on the metadata
# -----------------------------------------------------------------------------


def GenerateMetadataObject(tblName):

    # Generate a Metadata Object
    MD = MetaData()
    # Read Metadata from table
    file = open(GlobalCurrentDirectory + "/" + tblName, "r")
    MetaFromFile = file.readline()
    # Split the colums by |
    MetaSplitByPipe = MetaFromFile.split('|')
    # Split each colum into two {argument} {datatype}
    MetaArgs = []
    for i, _ in enumerate(MetaSplitByPipe):
        MetaArgs.append(MetaSplitByPipe[i].split())

    for i, _ in enumerate(MetaArgs):
        setattr(MD, MetaArgs[i][0], MetaArgs[i][1])

    setattr(MD, 'MetaArgsList', MetaArgs)

    return MD

# ----------------------------------------------------------------------------
# FUNCTION NAME:     CheckIfDataTypeMatches(InsertValue, ArgumentPair)
# PURPOSE:           This function checks if a value matches the correct data type
# -----------------------------------------------------------------------------


def CheckIfDataTypeMatches(InsertValue, ArgumentPair):
    if isint(InsertValue) and ArgumentPair[1] == 'int':
        # print (InsertValue + ArgumentPair[1] + "Are a match")
        return True

    elif isfloat(InsertValue) and ArgumentPair[1] == 'float':
        # print (InsertValue + ArgumentPair[1] + "Are a match")
        return True

    elif "char" in ArgumentPair[1] and InsertValue.startswith("'") and InsertValue.endswith("'"):
        # print (InsertValue + ArgumentPair[1] + "Are a match")
        MetaDataSearch = re.search(r'\((\d*)\)', ArgumentPair[1])
        if MetaDataSearch:
            MetaDataLength = MetaDataSearch.group(1)

            if len(InsertValue) <= int(MetaDataLength) + 2:
                return True
            else:
                return False
        else:
            return False
    else:
        return False

# Helps check if a value i a float


def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

# Helps check if a value is an int


def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b

# ----------------------------------------------------------------------------
# FUNCTION NAME:     InsertCommand(unalteredCommandLine, commandLine[2])
# PURPOSE:           This function executes the insert command
# -----------------------------------------------------------------------------


def InsertCommand(OGcommandLine, commandsList):

    tblName = commandsList[0].lower()
    # Find the text args between the parantheses
    InsertArgs = ParseCommandByPara(OGcommandLine)

    global GlobalCurrentDirectory
    if not GlobalCurrentDirectory:
        print("!Failed a database is currently not in use")
    else:
        # Create an object based on the metadata
        MDObject = GenerateMetadataObject(tblName)
        # Get the metadata list which contains the number of arguments
        MDargsList = getattr(MDObject, 'MetaArgsList')

        if len(InsertArgs) != len(MDargsList):
            print("!Failed Insert values contains incorrect number of arguments")

        else:
            # Check if the table/file exists
            if os.path.exists(GlobalCurrentDirectory + "/" + tblName):
                # append the add argument
                file = open(GlobalCurrentDirectory + "/" + tblName, "a")

                # Check that each variable is of the correct type
                VariablesChecked = True
                for i, _ in enumerate(InsertArgs):
                    if not CheckIfDataTypeMatches(InsertArgs[i], MDargsList[i]):
                        VariablesChecked = False

                # If the variables matched, insert the record
                if VariablesChecked:
                    file.write('\n')
                    for i, _ in enumerate(InsertArgs):
                        if len(InsertArgs) - 1 == i:
                            file.write(InsertArgs[i])
                        else:
                            file.write(InsertArgs[i] + "|")
                    print("1 new record inserted.")

                else:
                    print(
                        "!Failed the record was not inserted : Data entered did not match the metadata.")

                file.close()
            else:
                print("!Failed to modify table " +
                      tblName + " because it does not exist.")


# ----------------------------------------------------------------------------
# FUNCTION NAME:     AlterTable(tblName)
# PURPOSE:           This function executes the alter table command
# -----------------------------------------------------------------------------


def AlterTable(OGcommandLine, commandsList):

    if len(commandsList) > 4:
        tblName = commandsList[0].lower()
        Displaytblname = commandsList[0]

        # Find the text between the command ADD and ; for variable argument
        line = OGcommandLine.lower()
        line = re.search(r'add\s\s*(.*)\s*;', line).group(1)

        global GlobalCurrentDirectory
        if not GlobalCurrentDirectory:
            print("!Failed a database is currently not in use")
        else:
            # Check if the table/file exists
            if os.path.exists(GlobalCurrentDirectory + "/" + tblName):
                # append the add argument
                file = open(GlobalCurrentDirectory + "/" + tblName, "a")
                file.write(" | " + line)
                file.close()
                print("Table " + Displaytblname + " modified.")
            else:
                print("!Failed to modify table " +
                      Displaytblname + " because it does not exist.")

    else:
        print("!Failed invalid number of arguments")
# ----------------------------------------------------------------------------
# FUNCTION NAME:     DropTable(tblName)
# PURPOSE:           This function executes the drop table command
# -----------------------------------------------------------------------------


def DropTable(tblName):
    Displaytblname = tblName
    tblName = tblName.lower()

    global GlobalCurrentDirectory
    if not GlobalCurrentDirectory:
        print("!Failed a database is currently not in use")
    else:
        # Check if the table/file exists
        if os.path.exists(GlobalCurrentDirectory + "/" + tblName):
            try:
                os.remove(GlobalCurrentDirectory + "/" + tblName)
                print("Table " + Displaytblname + " deleted.")
            except:
                print("!Failed to delete the table due to an error")
        else:
            print("!Failed to delete " + Displaytblname +
                  " because it does not exist.")
# ----------------------------------------------------------------------------
# FUNCTION NAME:     DropDatabase(DBname)
# PURPOSE:           This function executes the drop database command
# -----------------------------------------------------------------------------


def DropDatabase(DBname):
    # Check if the folder exists
    if os.path.exists(DBname):

        try:
            # Remove directory
            shutil.rmtree(DBname)

            # If the global database was dropped, reset global variable
            global GlobalCurrentDirectory
            if GlobalCurrentDirectory == DBname:
                GlobalCurrentDirectory = ""

            print("Database " + DBname + " deleted.")
        except:
            print("!Failed to delete the database due to an error")

    else:
        print("!Failed to delete " + DBname + " because it does not exist.")
# ----------------------------------------------------------------------------
# FUNCTION NAME:     SelectCommand(commandsList)
# PURPOSE:           This function executes the select command
# -----------------------------------------------------------------------------


def SelectCommand(commandsList):

    global GlobalCurrentDirectory

    commandLine = ' '.join(str(e) for e in commandsList)

    # Check if the command has the format select name, name from table ;
    # Group 1 = name , name
    # Group 2 = tablename
    SelectCommand = re.search(
        r'(?i)select\s*(.*?)\s*from\s*(\w*)\s*;', commandLine)

    # Check if the command has the format select name, name from table where condition;
    # Group 1 = name , name
    # Group 2 = tablename
    # Group 3 = conditon
    SelectWhereCommand = re.search(
        r'(?i)select\s*(.*?)\s*from\s*(\w*)\s*where\s*(.*?)\s*;', commandLine)

    # The columns we want
    selectColumns = ''
    # The table name
    selectTableName = ''
    # The where condition if exists
    selectWhere = ''

    # Check if the regular expressions had a match if so populate the groups
    if SelectCommand:
        selectColumns = SelectCommand.group(1)
        selectTableName = SelectCommand.group(2).lower()
        print('Select without the where condition\n')
    elif SelectWhereCommand:
        selectColumns = SelectWhereCommand.group(1)
        selectTableName = SelectWhereCommand.group(2).lower()
        selectWhere = SelectWhereCommand.group(3)
        print('Select with the where condition')
    else:
        print('SELECT COMMAND NOT RECOGNIZED')

    # If either RE had a match grab the data from the file/table
    MetaDataFileLine = ''
    TableDataFileLines = ''
    if (SelectCommand and len(selectTableName) > 0 and len(selectColumns) > 0) or (SelectWhereCommand
                                                                                   and len(selectTableName) > 0 and len(selectColumns) > 0 and len(selectWhere) > 0):
        if not GlobalCurrentDirectory:
            print("!Failed a database is currently not in use")
        else:
            # Check if the table/file exists
            if not os.path.exists(GlobalCurrentDirectory + "/" + selectTableName):

                print("!Failed to query table " +
                      selectTableName + " because it does not exist.")

            else:
                # Grab table data and clean up
                file = open(GlobalCurrentDirectory +
                            "/" + selectTableName, "r")
                MetaDataFileLine = file.readline()
                TableDataFileLines = file.readlines()
                MetaDataFileLine = MetaDataFileLine.replace('\n', '')
                for i, _ in enumerate(TableDataFileLines):
                    TableDataFileLines[i] = TableDataFileLines[i].replace(
                        '\n', '')

                file.close()

                # If the command has *, display all with no where condition
                if SelectCommand and selectColumns == '*':
                    print(MetaDataFileLine)
                    for line in TableDataFileLines:
                        print(line)

                # If the command has column names, display only those ones with no where cond
                elif SelectCommand:
                    # MetaData Object to assist
                    MD = MetaData()
                    MD = GenerateMetadataObject(selectTableName)

                    # Split the entered columns by  ,
                    selectColumnsList = selectColumns.split(',')
                    # Remove any blanks
                    for i, _ in enumerate(selectColumnsList):
                        selectColumnsList[i] = selectColumnsList[i].strip()
                    # Split each table row in a list
                    for i, _ in enumerate(TableDataFileLines):
                        TableDataFileLines[i] = TableDataFileLines[i].split(
                            '|')

                    # IndexList will contain a list of indexes of the columns we want
                    # We can retrieve it based on the object and columns we want
                    IndexList = getIndexList(MD, selectColumnsList)

                    # Based on the indexList(cols we want) and TableData create a new list to display
                    NewTableList = getNewTableList(
                        IndexList, TableDataFileLines, False, [])

                    # Get Args List to search for column names
                    ObjectArgList = getattr(MD, 'MetaArgsList')

                    # Display column names
                    for i, _ in enumerate(NewTableList[0]):
                        tempStr = ' '.join(ObjectArgList[NewTableList[0][i]])
                        if len(NewTableList[0]) - 1 == i:
                            print(tempStr)
                        else:
                            print(tempStr + "|", end='')

                    for i in range(1, len(NewTableList)):
                        for j in range(len(NewTableList[i])):
                            if len(NewTableList[i]) - 1 == j:
                                print(NewTableList[i][j])
                            else:
                                print(NewTableList[i][j] + "|", end='')

                elif SelectWhereCommand:
                    #0:columnname , 1: operator , 2: condition
                    selectWhereList = selectWhere.split()
                    
                     # MetaData Object to assist
                    MD = MetaData()
                    MD = GenerateMetadataObject(selectTableName)

                    #Generate templist to look up index in table
                    tempList = list()
                    tempList.append(selectWhereList[0])
                    IndexList = getIndexList(MD, tempList)

                     # Split each table row in a list
                    for i, _ in enumerate(TableDataFileLines):
                        TableDataFileLines[i] = TableDataFileLines[i].split(
                            '|')

                    NewTableL = getNewTableList(IndexList, TableDataFileLines, True, selectWhereList)

                    print("Tes")

                # IF selectCouumns = name, name and selectWhereCommand = True
                    # Grab data from those colums
                    # Filter the data
                    # Display
    else:
        print("!Failed select command arguments were invalid")

# ----------------------------------------------------------------------------
# FUNCTION NAME:     getNewTableList(DBname)
# PURPOSE:           This function will return a new table list based on
#                    the index list we give it (remove columns)
# -----------------------------------------------------------------------------


def getNewTableList(IndexList, TableDataLines, isWhereActive, WhereCondition):

    #If there is a where condition
    if isWhereActive :
        tableList = list()
        # Append IndexList to index 0
        tableList.append(IndexList)

        # For every row
        for i, _ in enumerate(TableDataLines):
            # Create a row list
            rowList = TableDataLines[i]
            AddToList = False
            # For certain columns in the row
            for j, _ in enumerate(IndexList):
           
                SecondValue = float(WhereCondition[2])
                FirstValue = float(TableDataLines[i][IndexList[j]])
                if(op[WhereCondition[1]](FirstValue, SecondValue)) : 
                    AddToList = True

            # Append the row to the table list
            if AddToList :
                tableList.append(rowList)

        #List returned with items filter by the condition 
        return tableList
    else:
        tableList = list()
        # Append IndexList to index 0
        tableList.append(IndexList)

        # For every row
        for i, _ in enumerate(TableDataLines):
            # Create a row list
            rowList = list()
            # For certain columns in the row
            for j, _ in enumerate(IndexList):
                # print(TableDataLines[i][IndexList[j]], end=' | ')
                # Append the columns to the new row
                rowList.append(TableDataLines[i][IndexList[j]])
            # print('')
            # print(rowList)
            # Append the row to the table list
            tableList.append(rowList)

        return tableList




    

# ----------------------------------------------------------------------------
# FUNCTION NAME:     getIndexList(DBname)
# PURPOSE:           This function will return a list on indices corresponding
#                    to the location on the table
# -----------------------------------------------------------------------------


def getIndexList(MD, selectColumnsList):
    # MD is the metadata object
    # selectColumnsList is the list of columns we want

    # IndexList will contain a list of indices of the columns we want
    IndexList = []
    # Grab the list from the metadata object
    ObjectArgList = getattr(MD, 'MetaArgsList')
    # Find Indices from the object Ex: [0 , 2] columns 0 and 2
    for i, _ in enumerate(selectColumnsList):
        for j, _ in enumerate(ObjectArgList):
            if(selectColumnsList[i] == ObjectArgList[j][0]):
                IndexList.append(j)

    return IndexList

# ----------------------------------------------------------------------------
# FUNCTION NAME:     UseDatabase(DBname)
# PURPOSE:           This function executes the database use command
# -----------------------------------------------------------------------------


def UseDatabase(DBname):
    # Check if the folder exists
    if os.path.exists(DBname):
        global GlobalCurrentDirectory
        GlobalCurrentDirectory = DBname
        print("Using database " + DBname + ".")
    else:
        print("!Failed to use database " + DBname +
              " because it does not exist.")
# ----------------------------------------------------------------------------
# FUNCTION NAME:     ParseCommandByPara()
# PURPOSE:           This function parses a string for table creation, returns a list
# -----------------------------------------------------------------------------


def ParseCommandByPara(line):

    # Parse Everything within (.....); Then split by comma
    line = re.search(r'\((.*?)\);', line).group(1)
    line = line.split(',')

    # Remove any leading whitespaces
    for i, _ in enumerate(line):
        line[i] = line[i].strip()

    return line
# ----------------------------------------------------------------------------
# FUNCTION NAME:     CreateTable(tblName, OGCommandLine)
# PURPOSE:           This function executes the database creation command
# -----------------------------------------------------------------------------


def CreateTable(tblName, OGCommandLine):

    Displaytblname = tblName
    tblName = tblName.lower()

    global GlobalCurrentDirectory
    if not GlobalCurrentDirectory:
        print("!Failed a database is currently not in use")
    else:

        # Try and Parse the string "(arg arg arg);""
        argumentsParsed = True
        try:
            argumentList = ParseCommandByPara(OGCommandLine)

            # Check the number of args must be >= 2
            argumentsCheckList = []
            for i, _ in enumerate(argumentList):
                argumentsCheckList.append(argumentList[i].split())
                if len(argumentsCheckList[i]) < 2:
                    argumentsParsed = False

        # If it fails trigger flag
        except:
            argumentsParsed = False

        # Check if tblName is invalid or flag has been triggered
        if tblName == "(" or not tblName or argumentsParsed == False:
            print("!Failed a syntax error occured")

        else:
            # Check if the table/file exists
            if not os.path.exists(GlobalCurrentDirectory + "/" + tblName):

                file = open(GlobalCurrentDirectory + "/" + tblName, "w")
                print("Table " + Displaytblname + " created.")

                for i, _ in enumerate(argumentList):

                    if len(argumentList) - 1 == i:
                        file.write(argumentList[i])
                    else:
                        file.write(argumentList[i] + "|")

                file.close()
            else:
                print("!Failed to create table " +
                      Displaytblname + " because it already exists.")
# ----------------------------------------------------------------------------
# FUNCTION NAME:     CreateDatabase(DBname)
# PURPOSE:           This function executes the database creation command
# -----------------------------------------------------------------------------


def CreateDatabase(DBname):
    # First check if the DB name is invalid
    if DBname == ";" or not DBname:
        print("!Failed database name was invalid")

    else:
        # Check if the foler exists
        if not os.path.exists(DBname):
            os.mkdir(DBname)
            print("Database " + DBname + " created.")
        else:
            print("!Failed to create database " +
                  DBname + " because it already exists.")
# ----------------------------------------------------------------------------
# FUNCTION NAME:     ParseCommandByWord()
# PURPOSE:           This function parses a string by word and removes any
#                    blanks or spaces, returns a list
# -----------------------------------------------------------------------------


def ParseCommandByWord(line):
    # Split the input by word
    line = re.split(r'(\W+)', line)
    # Remove any leading whitespaces from the list
    for i, _ in enumerate(line):
        line[i] = line[i].strip()
    # Remove any blanks from the list
    line = list(filter(None, line))

    return line
# ----------------------------------------------------------------------------
# FUNCTION NAME:     ReadCommandsFileInput()
# PURPOSE:           This function reads the SQL test file input and parses it
#                    then returns a list of commands to be exected
# -----------------------------------------------------------------------------


def ReadCommandsFileInput():
    # Read in the file lines via standard input
    FileInputLines = sys.stdin.readlines()
    # New List which will contain the commands that will be executed
    FileInputCommands = []
    # New list to account for multiple lines
    MultiLineCommands = []

    for line in FileInputLines:
        # Ignore lines that are blank or are comments
        if line == '\r\n' or "--" in line or line == '\n':
            pass
        # Remove newline from current line and append to the commands list
        else:
            temp_line = line.replace('\r\n', '')
            temp_line = temp_line.replace('\t', '')
            temp_line = temp_line.replace('\n', '')
            FileInputCommands.append(temp_line)

    # Temporary variable to combine multi-line commands
    TemporaryString = ''
    for line in FileInputCommands:
        # ; indicates the end of the query
        if line.endswith(';'):
            MultiLineCommands.append(TemporaryString + line)
            TemporaryString = ''
        # Concat each line if it does not contain a ;
        else:
            TemporaryString = TemporaryString + line
            if(line == '.exit'):
                MultiLineCommands.append(line)

    return MultiLineCommands


if __name__ == "__main__":
    main()
