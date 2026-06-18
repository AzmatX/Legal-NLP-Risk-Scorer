from src.ingestion.cleaner import TextCleaner
from src.ingestion.schema import ContractSchema
from src.ingestion.validator import ContractValidator


class ContractProcessor:

    def __init__(self):
        self.cleaner = TextCleaner()
        self.validator = ContractValidator()

    def process_text(self, file_name: str, text: str):

        self.validator.validate(file_name, text)

        cleaned_text = self.cleaner.clean(text)

        structured_data = ContractSchema(
            file_name=file_name,
            text=cleaned_text,
            entities={},
            clauses={}
        )

        return structured_data.to_dict()