import csv
import os
from typing import Dict, List

BASE_URL = f"{os.path.dirname(os.path.realpath(__file__))}/resources"


def load_dict(language: str, file_name: str) -> Dict:

    with open(os.path.join(BASE_URL, language, file_name)) as csvfile:
        csv_reader = csv.reader(csvfile)
        result = {row[0]: float(row[1]) for row in csv_reader}

    return result


def load_string_file(language: str, file_name: str) -> List:
    with open(os.path.join(BASE_URL, language, file_name)) as str_file:
        result = [line.replace("\n", "") for line in str_file]

    return result
