import pytest
import csv
import mock
from unittest.mock import patch
import os
from ..DataFile import Metadata, DataFile, Relation, _convert_string_to_number

MANUFACTURER_VALUES = {"Toyota": 2, "Volkswagon": 1, "Ferrari": 1}
MODEL_VALUES = {"Camry": 1, "GTI": 1, "Corolla": 1, "Dino 246 GT": 1}
COLOR_VALUES = {"Gray": 1, "White": 1, "Black": 1, "Red": 1}
COST_QUANT_VALUES = ["$15,000", "$20,000", "$10,000"]
COST_QUAL_VALUES = {"N.A.": 1}
MPG_VALUES = [25.4, 23.2, 28.2, 18.2]
EMPTY_VALUES = {}
'''
Return a very simple, fake CSV file for testing
'''
@pytest.fixture()
def simple_csv():
    data = (
        'Manufacturer,Model,Color,Miles,MPG,Cost\n'
        'Toyota,Camry,Gray,"75,000","25.4","$15,000"\n'
        'Volkswagon,GTI,White,"75,000","23.2","$20,000"\n'
        'Toyota,Corolla,Black,"100,000","28.2","$10,000"\n'
        'Ferrari,Dino 246 GT,Red,"252,346","18.2",N.A.\n'
        )
    return mock.mock_open(read_data=data)

def create_simple_csv(file_name="../test_data/simple.csv"):
    data = [
        ['Manufacturer','Model','Color','Miles','MPG','Cost'],
        ['Toyota','Camry','Gray','75,000','25.4','$15,000'],
        ['Volkswagon','GTI','White','75,000','23.2','$20,000'],
        ['Toyota','Corolla','Black','100,000','28.2','$10,000'],
        ['Ferrari','Dino 246 GT','Red','252,346','18.2','N.A.'],
        ]
    if not os.path.isfile(file_name):
        test_file = open(file_name, "w", newline="\n")
        writer = csv.writer(test_file)
        writer.writerows(data)
        test_file.close()

@pytest.fixture()
def update_cost_csv():
    data = (
        'Manufacturer,Model,Color,Miles,MPG,Cost\n'
        'Toyota,Camry,Gray,"75,000",25.4,"$15,000"\n'
        'Volkswagon,GTI,White,"75,000",23.2,"$20,000"\n'
        'Toyota,Corolla,Black,"100,000",28.2,"$10,000"\n'
        'Ferrari,Dino 246 GT,Red,"252,346",18.2,-1\n'
        )
    return mock.mock_open(read_data=data)

@pytest.fixture()
def update_miles_csv():
    data = (
        'Manufacturer,Model,Color,Miles,MPG,Cost\n'
        'Toyota,Camry,Gray,"76,000",25.4,"$15,000"\n'
        'Volkswagon,GTI,White,"75,000",23.2,"$20,000"\n'
        'Toyota,Corolla,Black,"100,000",28.2,"$10,000"\n'
        'Ferrari,Dino 246 GT,Red,"252,346",18.2,N.A.\n'
        )
    return mock.mock_open(read_data=data)

'''
Build a test string for the metadata
'''
def build_metadata_string(number, name, datatype, qual_values:dict, quant_values:list):
    string = f"\n<Metadata for column number {number}: {name}> datatype:{datatype}"
    if qual_values:
        string = string + f"; qual_values_count:{len(qual_values.keys())}"
    if quant_values:
        string = string + f"; quant_values_count:{len(quant_values)}"
    if qual_values:
        string = string + f"\nQualitative Values ['Value': count]: {qual_values}"
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
    assert(run_metadata_asserts(test_file.Miles, 3, "Miles", EMPTY_VALUES, 4, "quantitative"))
    assert(run_metadata_asserts(test_file.MPG, 4, "MPG", EMPTY_VALUES, 4, "quantitative"))
    assert(run_metadata_asserts(test_file.Cost, 5, "Cost", {"N.A.": 1}, 3, "both"))

def test_create_file(mocker, simple_csv):
    mocker.patch('builtins.open', simple_csv)
    test_file = DataFile("../test_data/Data.csv")
    alt_file = DataFile.create("../test_data/Data.csv")

    assert(test_file == alt_file)

def test_show_metadata_qual_data(mocker, simple_csv):
    mocker.patch('builtins.open', simple_csv)
    test_file = DataFile("../test_data/Data.csv")

    MANUFACTURER_META_REPORT = build_metadata_string(0, "Manufacturer", "qualitative", MANUFACTURER_VALUES, EMPTY_VALUES)
    manufacturer_report = test_file.show_metadata("Manufacturer")
    assert(MANUFACTURER_META_REPORT == manufacturer_report)

def test_show_metadata_quant_data(mocker, simple_csv):
    mocker.patch('builtins.open', simple_csv)
    test_file = DataFile("../test_data/Data.csv")

    MPG_META_REPORT = build_metadata_string(4, "MPG", "quantitative", EMPTY_VALUES, MPG_VALUES)
    MPG_report = test_file.show_metadata("MPG")
    assert(MPG_META_REPORT == MPG_report)

def test_show_metadata_both_data(mocker, simple_csv):
    mocker.patch('builtins.open', simple_csv)
    test_file = DataFile("../test_data/Data.csv")

    COST_META_REPORT = build_metadata_string(5, "Cost", "both", COST_QUAL_VALUES, COST_QUANT_VALUES)
    cost_report = test_file.show_metadata("Cost")
    assert(COST_META_REPORT == cost_report)

def test_update_column_value_no_kwargs(update_cost_csv):
    test_file = "../test_data/simple.csv"
    create_simple_csv(test_file)
    destination_file = "update_column_test.csv"
    data_file = DataFile(test_file)
    data_file.update_value("N.A.", -1,"Cost", new_file_name=destination_file)
    test_file = open("../test_data/" + destination_file, "r")
    with patch("builtins.open", update_cost_csv):
        with open("../test_data/simple.csv", "r") as correct_file:
            test_lines = test_file.readlines()
            for test_line in test_lines:
                correct_line = correct_file.readline()
                #print(test_line)
                #print(correct_line)
                assert(test_line == correct_line)
    test_file.close()
    os.remove("../test_data/" + destination_file)
    os.remove("../test_data/simple.csv")

def test_update_column_value_kwargs(update_miles_csv):
    test_file = "../test_data/simple.csv"
    create_simple_csv(test_file)
    destination_file = "update_column_test.csv"
    data_file = DataFile(test_file)
    data_file.update_value(75000, 76000,"Miles", new_file_name=destination_file, Model="Camry")
    test_file = open("../test_data/" + destination_file, "r")
    with patch("builtins.open", update_miles_csv):
        with open("../test_data/simple.csv", "r") as correct_file:
            test_lines = test_file.readlines()
            for test_line in test_lines:
                correct_line = correct_file.readline()
                #print(test_line)
                #print(correct_line)
                assert(test_line.replace(",", "").replace("$", "").replace('"', "") == correct_line.replace(",", "").replace("$", "").replace('"', ""))
    test_file.close()
    os.remove("../test_data/" + destination_file)
    os.remove("../test_data/simple.csv")



