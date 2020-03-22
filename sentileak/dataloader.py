import csv
import os
from typing import Dict, List

BASE_URL = f"{os.path.dirname(os.path.realpath(__file__))}/data"


def load_dict(language: str, file_name: str) -> Dict:
    """
    Method to load dictionaries from a file
    :param language: language of the dictionary to load
    :param file_name: name of the file to load
    :return: a dictionary with the file content
    """

    with open(os.path.join(BASE_URL, language, file_name)) as csvfile:
        csv_reader = csv.reader(csvfile)
        result = {row[0]: float(row[1]) for row in csv_reader}

    return result


def load_string_file(language: str, file_name: str) -> List[str]:
    """
    Method to load a list of string that represents the lines of a file
    :param language: language of the file to load
    :param file_name: name of the file to load
    :return: a list with the lines of the file
    """
    with open(os.path.join(BASE_URL, language, file_name)) as str_file:
        result = [line.replace("\n", "") for line in str_file]

    return result
