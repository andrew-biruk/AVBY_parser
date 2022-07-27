from csv import reader
from json import load, dumps
from prettytable import from_csv, from_json


def pretty_print(file_name: str) -> None:
    """prettytable module must be installed for successful call"""
    def print_json():
        with open(file_name, encoding="utf-8") as json_f:
            return from_json(dumps(load(json_f)))

    def print_csv():
        with open(file_name, newline="") as csv_f:
            return from_csv(csv_f)

    extension: str = file_name.split(".")[-1]
    options = {"json": print_json, "csv": print_csv}
    print(f"FILE: {file_name}")
    print(options[extension]())


def regular_print(file_name: str) -> None:
    def print_json():
        with open(file_name, encoding="utf-8") as json_f:
            data = load(json_f)
            return dumps(data, indent=2, sort_keys=True)

    def print_csv():
        with open(file_name, newline="") as csv_f:
            file = reader(csv_f, delimiter=' ', quotechar='|')
            return "\n".join([" ".join(i.split(";")) for line in file for i in line])

    extension: str = file_name.split(".")[-1]
    options = {"json": print_json, "csv": print_csv}
    print(f"FILE: {file_name}")
    print(options[extension]())

file = input("Enter file name >> ")
pretty_print(file)
regular_print(file)
