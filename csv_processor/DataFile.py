import csv
import os
import shutil
import tempfile
from pathlib import Path
#from collections import OrderedDict
'''
    Remove chars , and $ from a string
'''
def _convert_to_decimal_string(value):
    return value.replace(",", "").replace("$", "")
'''
    Return true if param value can be converted to a number
'''
def _is_decimal(value):
    return _convert_to_decimal_string(value).replace("-", "0", 1).replace(".", "0", 1).isdecimal()
'''
    Convert param value to int or float, depending on the string
'''
def _convert_string_to_number(value):
    if not _is_decimal(value):
        raise TypeError(f"{value} cannot be converted to int or float.")
    number_string = _convert_to_decimal_string(value)
    if number_string.count(".") == 0:
        return int(number_string)
    elif number_string.count(".") == 1:
        return float(number_string)
    else:
        raise TypeError(f"{value} cannot be converted to int or float.")
    

'''
Class to track column metadata information
The metadata tracked is:

column_name: the column header
column_number: the column number
'''
class Metadata:
    def __init__(self, column_name:str, column_number:int):
        self.name = column_name
        self.number = column_number
        self.qualitative_values = {} #dictionary; key is qualitative value, value is count
        self.quantitative_values_count = 0
        self.datatype = None #qualitative(numbers), quantitative(string), or both

    def __repr__(self):
        rep = f"<Metadata for column number {self.number}: {self.name}> datatype:{self.datatype}"
        if self.qualitative_values:
            rep = rep + f"; qual_values_count:{len(self.qualitative_values.keys())}"
        if self.quantitative_values_count:
            rep = rep + f"; quant_values_count:{self.quantitative_values_count}"
        return rep

    def __str__(self):
        report = self.__repr__()
        if self.qualitative_values:
            report = report + f"\nQualitative Values ['Value': count]: {self.qualitative_values}"
        return report

    def __eq__(self, other):
        return  self.name == other.name\
            and self.number == other.number\
            and self.qualitative_values == other.qualitative_values\
            and self.quantitative_values_count == other.quantitative_values_count\
            and self.datatype == other.datatype

'''
Class to track file information
'''
class BaseFile:
    def __init__(self, file_path:str, *args, **kwargs):
        self.file = file_path
        #key: column header, value: Metadata object
        self.headers = {}
        with open(self.file, "r") as f:
            reader = csv.reader(f, **kwargs)
            self._number_columns = -1
            self._number_rows = 0
            header_list = None
            first_row = next(reader)
            self._number_columns = len(first_row)
            #populate dictionary for headers
            for col in range(self._number_columns):
                self.headers[first_row[col]] = Metadata(first_row[col], col)
            header_list = list(self.headers.keys())
            #next(reader)
            #populate metadata for each column by analyzing each row in file
            for row in reader:
                #inner loop to check column values in row
                for index in range(len(header_list)):
                    header = header_list[index]
                    value = row[index]
                    meta = self.headers[header]
                    #determine if row value is quantitative (numerical) or quantitative, and update Metadata.datatype
                    if not _is_decimal(value):
                        if value in meta.qualitative_values.keys():
                            meta.qualitative_values[value] += 1
                        else:
                            meta.qualitative_values[value] = 1
                        if meta.datatype is None:
                            meta.datatype = "qualitative"
                        elif meta.datatype == "quantitative":
                            meta.datatype = "both"
                    else:
                        if meta.datatype is None:
                            meta.datatype = "quantitative"
                        elif meta.datatype == "qualitative":
                            meta.datatype = "both"
                        meta.quantitative_values_count += 1
        self._number_rows = reader.line_num
        #For each value in headers, set an attribute with the same name as that header that returns the associated set
        for header, value in self.headers.items():
            setattr(self, header.replace(" ", "_"), value)

    '''
    Return a metadata summary for given column. If no column is provided, returns the summary for each column.
    '''
    def show_metadata(self, *columns:str):
        report = ""
        if columns:
            for column in columns:
                if column in self.headers.keys():
                    report = report + f"\n{self.headers[column].__str__()}"
                    continue
                else:
                    report = report + f"\n{column} is not a valid column name."
            return report
        for column, meta in self.headers.items():
            report = report + f"\n{meta.__str__()}"
        return report

    def __eq__(self, other):
        return self.file == other.file and self.headers == other.headers

'''
Class to define a relationship between a value in 1 column and values from another column
'''
class Relation:
    def __init__(self, value:str, column:Metadata, relational_column:Metadata, file:str):
        if value not in column.qualitative_values:
            raise IndexError(f"{value} not a qualitative value of {column.name}.")
        self.value = value
        self.related_values = set()
        self.column_name = column.name
        self.column_number = column.number
        self.related_name = relational_column.name
        self.related_number = relational_column.number
        self.type = None
        with open(file, "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if row[self.column_number] == self.value:
                    self.related_values.add(row[relational_column.number])
        self.type = f"one to {len(self.related_values)}"

    def __str__(self):
        return f"<Relation between {self.value} from {self.column_name} and {self.related_name}> {self.type}."

    def __repr__(self):
        return self.__str__() + "\nRelated Values: " + ",".join(self.related_values)

    def __eq__(self, other):
        return  self.value == other.value\
            and self.related_values == other.related_values\
            and self.column_name == other.column_name\
            and self.column_numebr == other.column_number\
            and self.related_name == other.related_name\
            and self.related_number == other.related_number\
            and self.type == other.type



'''
Class to represent a csv file with data in it
'''
class DataFile(BaseFile):
    '''
    Ensures that file exists and stores column names and unique non numeric row values.

    file_path: string descripting path to csv file to read
    file_type: passed to csv.reader as dialect parameter. Default is excel.
    **kwargs: passed to csv.reader as format parameters. See python csv.
    '''
    def __init__(self, file_path:str, *args, **kwargs):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"{file_path} does not exist.")
        super().__init__(file_path)
        self.relationships = {}
    '''
    Wrapper for __init__ for performance benchmarking.
    '''
    def create(*args, **kwargs):
        return DataFile(*args, **kwargs)

    def __repr__(self):
        rep = f"DataFile {self.file}: {self._number_rows} rows; {self._number_columns} columns'\n'Headers:"
        for header, values in self.headers.items():
            rep = rep + f"\n<{header}>: {values.__repr__()}"
        return rep

        
    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return super().__eq__(other) and self.relationships == other.relationships

    '''
    Return relationship information between two columns
    '''
    def get_relationships(self, column1:str, column2:str) -> dict:
        left_col = self.headers[column1]
        right_col = self.headers[column2]
        for value in left_col.qualitative_values:
            self.relationships[value] = Relation(value, left_col, right_col, self.file)
        return self.relationships
    '''
    Return Relation between given value in given column with another column
    '''
    def get_relationship(self, value, column1:str, column2:str):
        left_col = self.headers[column1]
        right_col = self.headers[column2]
        relation = Relation(value, left_col, right_col, self.file)
        self.relationships[value] = relation
        return relation

    '''
    Update a value based on either the column, or specific values from other columns.
    Useful for replacing qualitative that should be a quantifiable number.
    '''
    def update_value(self, old_value, new_value, *columns, new_file_name=None, **column_value):
        in_file = Path(self.file).resolve()
        out_file = self.file
        directory = os.path.dirname(self.file)
        if new_file_name:
            out_file = directory + "/" + new_file_name
            out_file = Path(out_file).resolve()
        for column in columns:
            if column not in self.headers.keys():
                print(f"{column} is not a valid column.")
                return
        for column in column_value.keys():
            if column not in self.headers.keys():
                print(f"{column} is not a valid column.")
                return
        if not os.path.isfile(out_file):
            new_file = open(out_file,"w")
            new_file.close()
        with in_file.open("r") as real_file, tempfile.TemporaryFile(mode="w", dir=in_file.parent, delete=False, newline="\n") as temp_csv:
            reader = csv.DictReader(real_file)
            writer = csv.DictWriter(temp_csv, fieldnames = [header for header in self.headers.keys()])
            writer.writeheader()
            for row in reader:
                alter_row = True
                #check row column values against column_value dict
                for column, val in column_value.items():
                    #check actual value against column_value
                    actual_value = row[column]
                    if _is_decimal(actual_value):
                        actual_value = _convert_to_decimal_string(actual_value)
                    #print(f"Column: {column}\tCurrent Value: {actual_value}\tTest Value:{val}")
                    if actual_value != val:
                        alter_row = False
                        break
                if alter_row:
                    #print(row)
                    for column in columns:
                        current_value = row[column]
                        if _is_decimal(current_value):
                            current_value = _convert_string_to_number(current_value)
                        #print(f"current_value: {current_value}\told_value: {old_value}\tnew_value: {new_value}")
                        if current_value == old_value:
                            row[column] = new_value
                writer.writerow(row)
        #close tempfile before using shutil.copyfile
        _ = shutil.copyfile(temp_csv.name, out_file)
        os.remove(temp_csv.name)

    '''
    Reinitialize DataFile to a new file, keeping any relationships that have been run.
    '''
    def update_file(self, new_file):
        pass

    '''
    Filter data based on criteria passed to column_values. Currently only supports exact matches of qualitative data.
    '''
    def filter(self, *args, save_file=None, **column_values):
        for key in column_values.keys():
            if key not in self.headers.keys():
                raise KeyError(f"Column {key} is not valid.")
        data = Path(self.file).resolve()
        filtered = tempfile.TemporaryFile(mode="w", dir=data.parent, delete=False, newline="\n")
        with data.open("r") as in_file:
            reader = csv.DictReader(in_file)
            writer = csv.DictWriter(filtered, self.headers.keys())
            writer.writeheader()
            for row in reader:
                pass_test = True
                for column, test_value in column_values.items():
                    row_value = row[column]
                    if _is_decimal(row_value):
                        row_value = _convert_string_to_number(row_value)
                    if test_value != row_value:
                        pass_test = False
                        break
                if pass_test:
                    writer.writerow(row)
        filtered.close()
        if save_file:
            path = str(data.parent) + f"/{save_file}"
            if not os.path.isfile(path):
                f = open(path, "w")
                f.close()
            shutil.copyfile(filtered.name, Path(path).resolve())
        else:
            with open(filtered.name, "r") as report:
                reader = csv.reader(report)
                length = shutil.get_terminal_size(fallback=(100, 100))[0] / self._number_columns
                formatting = ""
                for num in range(self._number_columns):
                    formatting = formatting + "{" + str(num) + ":" + str(length) + "}"
                for row in reader:
                    print(formatting.format(*row))
        filtered.close()
        os.remove(filtered.name)



if __name__ == '__main__':
    file_path = os.path.dirname(__file__) + "/Data.csv"
    data = DataFile(file_path)
    print(data)
    r = data.get_relationship("Capital investment", "Measure", "Units")
    print(r.__repr__())

