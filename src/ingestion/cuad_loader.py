import json


class CUADLoader:

    def load(self, file_path: str):

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        contracts = []

        for contract in data["data"]:

            title = contract["title"]

            for paragraph in contract["paragraphs"]:

                contracts.append({
                    "title": title,
                    "context": paragraph["context"],
                    "qas": paragraph["qas"]
                })

        return contracts