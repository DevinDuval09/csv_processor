import pytest
import mock
from ..DataFile import Metadata, DataFile, Relation

MANUFACTURER_VALUES = {"Toyota": 2, "Volkswagon": 1}
MODEL_VALUES = {"Camry": 1, "GTI": 1, "Corolla": 1}
COLOR_VALUES = {"Gray": 1, "White": 1, "Black": 1}
COST_VALUES = ["$15,000", "$20,000", "$10,000"]
EMPTY_VALUES = {}
'''
Return a very simple, fake CSV file for testing
'''
@pytest.fixture()
def simple_csv():
    data = (
        "Manufacturer,Model,Color,Miles,MPG,Cost\n"
        "Toyota,Camry,Gray,75,000,25.4,$15,000\n"
        "Volkswagon,GTI,White,75,000,23.2,$20,000\n"
        "Toyota,Corolla,Black,100,000,28.2,$10,000\n"
        )
    return mock.mock_open(read_data=data)

'''
Build a test string for the metadata
'''
def build_metadata_string(number, name, datatype, qual_values:dict, quant_values:list):
    string = f"\n<Metadata for column number {number}: {name}> datatype:{datatype}"
    if quant_values:
        string = string + f"; quant_values_count:{len(quant_values)}"
    if qual_values:
        string = string + f"; qual_values_count:{len(qual_values.keys())}\nQualitative Values ['Value': count]: {qual_values}"
    return string

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

    assert(run_metadata_asserts(test_file.Manufacturer, 0, "Manufacturer", MANUFACTURER_VALUES, 0, "qualitative"))
    assert(run_metadata_asserts(test_file.Model, 1, "Model", MODEL_VALUES, 0, "qualitative"))
    assert(run_metadata_asserts(test_file.Color, 2, "Color", COLOR_VALUES, 0, "qualitative"))
    assert(run_metadata_asserts(test_file.Miles, 3, "Miles", EMPTY_VALUES, 3, "quantitative"))
    assert(run_metadata_asserts(test_file.MPG, 4, "MPG", EMPTY_VALUES, 3, "quantitative"))
    assert(run_metadata_asserts(test_file.Cost, 5, "Cost", EMPTY_VALUES, 3, "quantitative"))

def test_create_file(mocker, simple_csv):
    mocker.patch('builtins.open', simple_csv)
    test_file = DataFile("../test_data/Data.csv")
    alt_file = DataFile.create("../test_data/Data.csv")

    assert(test_file == alt_file)

def print_to_string(*args, **kwargs):
    output = io.StringIO()
    print(*args, file=output, **kwargs)
    string = output.getvalue()
    output.close()
    return string

def test_show_metadata_qual_data(mocker, simple_csv):
    mocker.patch('builtins.open', simple_csv)
    test_file = DataFile("../test_data/Data.csv")

    MANUFACTURER_META_REPORT = build_metadata_string(0, "Manufacturer", "qualitative", MANUFACTURER_VALUES, EMPTY_VALUES)
    manufacturer_report = test_file.show_metadata("Manufacturer")
    assert(MANUFACTURER_META_REPORT == manufacturer_report)

def test_show_metadata_quant_data(mocker, simple_csv):
    mocker.patch('builtins.open', simple_csv)
    test_file = DataFile("../test_data/Data.csv")

    COST_META_REPORT = build_metadata_string(5, "Cost", "quantitative", EMPTY_VALUES, COST_VALUES)
    Cost_report = test_file.show_metadata("Cost")
    assert(COST_META_REPORT == Cost_report)


