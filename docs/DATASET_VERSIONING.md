# Dataset Versioning

## Dataset Information

- Dataset Name: CUAD (Contract Understanding Atticus Dataset)
- Version: CUADv1
- Source: The Atticus Project
- Total Contracts Parsed: 510
- Annotation Categories: 41 Legal Categories

---

## Dataset Files

| File Name | Purpose |
|------------|----------|
| CUADv1.json | Complete Dataset |
| train_separate_questions.json | Training Data |
| test.json | Testing Data |

---

## Dataset Structure

CUADv1.json

data
 ├── title
 └── paragraphs
      ├── context
      └── qas

---

## Preprocessing Status

### Day 1
- Implemented ContractSchema
- Implemented TextCleaner
- Implemented ContractProcessor

### Day 2
- Added ContractValidator
- Added validation checks
- Tested cleaning and validation pipeline

### Day 3
- Analyzed CUAD dataset structure
- Implemented CUADLoader
- Parsed all 510 contracts
- Tested extraction of context and QAs

---

## Version History

### Version 1.0

- Initial dataset integration completed
- Cleaning pipeline completed
- Validation pipeline completed
- CUAD parser implemented
- Parsing tests completed

---

## Notes

This dataset is used for legal contract intelligence, clause extraction, risk scoring, and NLP model training.