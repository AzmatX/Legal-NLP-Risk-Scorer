from src.ingestion.cleaner import TextCleaner
from src.ingestion.schema import ContractSchema

class ContractProcessor:

    def __init__(self):
        self.cleaner = TextCleaner()

    def process_text(self, file_name: str, text: str):

        cleaned_text = self.cleaner.clean(text)

        structured_data = ContractSchema(
            file_name=file_name,
            text=cleaned_text,
            entities={},
            clauses={}
        )

        return structured_data.to_dict()