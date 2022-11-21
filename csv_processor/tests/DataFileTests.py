import pytest
import mock
from ..DataFile import Metadata, DataFile, Relation

'''
Return a very simple, fake CSV file for testing
'''
@pytest.fixture()
def simple_csv():
    data = (
        "Manufacturer,Model,Color,Miles,MPG,Cost\n"
        "Toyota,Camry,Gray,75000,25.4,$15000\n"
        "Volkswagon,GTI,White,75000,23.2,$20000\n"
        "Toyota,Corolla,Black,100000,28.2,$10000\n"
        )
    return mock.mock_open(read_data=data)

'''
Build a test string for the metadata
'''
def build_metadata_string(number, name, datatype, qual_values:dict, quant_values:dict):
    string = f"<Metadata for column number {number}: {name}> datatype:{datatype} "
    if quant_values:
        string = string + f"; quant_values_count:{len(quant_values.keys())}"
    if qual_values:
        string = string + f"; qual_values_count:{len(qual_values.keys())}\nValues: {qual_values}"
'''
Test validity of metadata object
'''
def run_metadata_asserts(metadata, number, name, correct_qual_values:dict, quant_count, datatype):
    assert(metadata.name == name)
    assert(metadata.number == number)
    assert(metadata.qualitative_values == correct_qual_values)
    assert(metadata.datatype == datatype)
    assert(metadata.quantitative_values_count == quant_count)
    return True

'''
Test init to:

-Make sure that column titles are added as attributes
-Make sure data populates correctly
'''
def test_init(mocker, simple_csv):
    mocker.patch('builtins.open', simple_csv)
    test_file = DataFile("../test_data/Data.csv")

    MANUFACTURER_VALUES = {"Volkswagon": 1, "Toyota": 2}
    MODEL_VALUES = {"Camry": 1, "GTI": 1, "Corolla": 1}
    COLOR_VALUES = {"Gray": 1, "White": 1, "Black": 1}
    EMPTY_VALUES = {}
    assert(run_metadata_asserts(test_file.Manufacturer, 0, "Manufacturer", MANUFACTURER_VALUES, 0, "qualitative"))
    assert(run_metadata_asserts(test_file.Model, 1, "Model", MODEL_VALUES, 0, "qualitative"))
    assert(run_metadata_asserts(test_file.Color, 2, "Color", COLOR_VALUES, 0, "qualitative"))
    assert(run_metadata_asserts(test_file.Miles, 3, "Miles", EMPTY_VALUES, 3, "quantitative"))
    assert(run_metadata_asserts(test_file.MPG, 4, "MPG", EMPTY_VALUES, 3, "quantitative"))
    assert(run_metadata_asserts(test_file.Cost, 5, "Cost", EMPTY_VALUES, 3, "quantitative"))

