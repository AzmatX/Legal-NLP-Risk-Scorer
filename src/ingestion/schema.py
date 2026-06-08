from dataclasses import dataclass, asdict

@dataclass
class ContractSchema:
    file_name: str
    text: str
    entities: dict
    clauses: dict

    def to_dict(self):
        return asdict(self)