from DataFile import DataFile
'''
Class to return filtered data from a DataFile

*non_equality_statements: string that outlines a single test to perform. For example, "Year>=2000".
Not regex supported.
**equality_tests: key is the name of a column, value is the value to test for equality
'''
class Filter:
    comparators = {
        ">=": "__ge__",
        "<=": "__le__",
        "=" : "__eq__",
        "==": "__eq__",
        ">" : "__gt__",
        "<" : "__lt__",
        "!=": "__eq__"
    }
    def __init__(self, data:DataFile, *non_equality_statements, **equality_tests):
        self.file = data
        #list of tuples. tuple data is (column name, operator, value) and is used to create tests.
        self.statements = []
    '''
    Run an individual test.
    TODO: determine types and type casting
    '''
    def _run_test(self, row_value, test, test_value):
        test = getattr(row_value, test)
        return test(test_value)
    '''
    Conduct all the statements on a row. Return true if they all pass.
    '''
    def _test_row(self, row):
        try:
            for statement in self.statements:
                row_value = row[statement[0]]
                test = Filter.comparators[statement[1]]
                test_val = statement[2]
                result = self._run_test(row_value, test, test_val)
                if "!" in statement[1] and result:
                    return False
                if not result:
                    return False
            return True
        except Exception:
            raise ValueError("No statements have been provided.")
        
    '''
    Load equality_tests as tuples into self.statements
    '''
    def _handle_kwargs(self, **equality_tests):
        for key, value in equality_tests.items():
            self.statements.append((key, "=", value))
    '''
    Load non_equality_statements into as tuples into self.statements
    '''
    def _handle_args(self, *args):
        for arg in args:
            self.statements.append(Filter._arg_parser(arg))
    '''
    Split a string argument into a tuple containing the column name, operator, and value.
    For example, passing "Year>=2000" would return ("Year", ">=", "2000").
    '''
    @staticmethod
    def _arg_parser(arg:str):
        operator_start = float("inf")
        value_start = 0
        for index in range(len(arg)):
            if (60 <= ord(arg[index]) <= 62) or ord(arg[index]) == 33:
                operator_start = int(min(operator_start, index))
            elif operator_start < float("inf"):
                value_start = index
                break
        return (arg[:operator_start], arg[operator_start:value_start], arg[value_start:])
