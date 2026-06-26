"""
Test the pipeline on both low‑risk and high‑risk sample contracts.
"""
import json
from src.clause_classifier import classify_contract
from src.risk_scoring.service import score_contract

def read_contract_file(filename: str) -> str:
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def test_contract(filename: str):
    print(f"\n{'='*60}")
    print(f"Testing: {filename}")
    print('='*60)
    
    text = read_contract_file(filename)
    clause_result = classify_contract(text)
    risk = score_contract(clause_result)
    
    print(f"\n📈 Risk Score: {risk['risk_score']}/100")
    print(f"🏷️  Risk Level: {risk['risk_level'].upper()}")
    
    if risk['missing_clauses']:
        print(f"⚠️  Missing mandatory: {', '.join(risk['missing_clauses'])}")
    
    if risk['recommendations']:
        print("💡 Recommendations:")
        for rec in risk['recommendations']:
            print(f"   ✓ {rec}")
    
    # Save detailed output to a file
    out_filename = filename.replace('.txt', '_output.json')
    with open(out_filename, 'w') as f:
        json.dump(risk, f, indent=2)
    print(f"✅ Detailed output saved to {out_filename}")

if __name__ == "__main__":
    test_contract("contract_low_risk.txt")
    test_contract("contract_high_risk.txt")