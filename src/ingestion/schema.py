from dataclasses import asdict, dataclass


@dataclass
class ContractSchema:
    file_name: str
    text: str
    entities: dict
    clauses: dict

    def to_dict(self):
        return asdict(self)