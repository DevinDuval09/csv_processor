import csv
import os
#from collections import OrderedDict
'''
Class to track column metadata information
The metadata tracked is:

name: the column header
number: the column number
qualitative values: a set containing all of the qualitative values
quantitative_values_count: the number of quantitative values in the column
datatype: datatype can be quantitative (all numerical), qualitative(strings), or both
'''
class Metadata:
    def __init__(self, column_name:str, column_number:int):
        self.name = column_name
        self.number = column_number
        self.qualitative_values = {}
        self.quantitative_values_count = 0
        self.datatype = None

    def __repr__(self):
        return f"<Metadata for column number {self.number}: {self.name}> datatype:{self.datatype}; qual_values_count:{len(self.qualitative_values.keys())}"

    def __str__(self):
        report = self.__repr__()
        report = report + f"\nValues: {self.qualitative_values}"
        return report

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
            next(reader)
            #populate metadata for each column by analyzing each row in file
            for row in reader:
                #inner loop to check column values in row
                for index in range(len(header_list)):
                    header = header_list[index]
                    value = row[index]
                    meta = self.headers[header]
                    #determine if row value is quantitative (numerical) or quantitative, and update Metadata.datatype
                    if not value.replace("-", "0", 1).replace(".", "0", 1).replace(",", "0").isdecimal():
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
    Return a metadata summary for given column. If no column is provided, returns the summary for each column.
    '''
    def get_metadata(self, *columns:str):
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


if __name__ == '__main__':
    file_path = os.path.dirname(__file__) + "/Data.csv"
    data = DataFile(file_path)
    print(data)
    r = data.get_relationship("Capital investment", "Measure", "Units")
    print(r.__repr__())

