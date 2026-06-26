"""
Test the full contract intelligence pipeline with a generated sample contract.
"""
import json
from src.clause_classifier import classify_contract
from src.risk_scoring.service import score_contract


def generate_sample_contract() -> str:
    """
    Builds a legal contract with:
    - Multiple sections (headings)
    - High‑risk clauses (Termination, Indemnification)
    - Some mandatory clauses (Confidentiality, Payment Terms)
    - Omitted mandatory clause (Governing Law) → to trigger missing penalty
    """
    return """
    MASTER SERVICE AGREEMENT

    ARTICLE 1: DEFINITIONS
    1.1 "Services" means the work described in Exhibit A.
    1.2 "Term" means the period specified in Section 2.

    ARTICLE 2: TERM
    This Agreement shall commence on the Effective Date and continue for one (1) year,
    unless earlier terminated as provided herein.

    ARTICLE 3: PAYMENT TERMS
    Client shall pay Contractor the fees set forth in Exhibit B within thirty (30) days
    of receipt of an invoice.

    ARTICLE 4: CONFIDENTIALITY
    Recipient agrees to hold all Confidential Information in strict confidence and
    not to disclose it to any third party.

    ARTICLE 5: TERMINATION FOR CAUSE
    Either party may terminate this Agreement immediately upon written notice if the
    other party breaches any material term and fails to cure such breach within
    thirty (30) days.

    ARTICLE 6: INDEMNIFICATION
    Contractor shall indemnify, defend, and hold harmless Client from and against
    any claims arising out of Contractor's performance under this Agreement.

    ARTICLE 7: LIMITATION OF LIABILITY
    In no event shall either party be liable for indirect, incidental, or consequential
    damages. Total liability shall not exceed the fees paid.

    ARTICLE 8: FORCE MAJEURE
    Neither party shall be liable for delays or failures in performance resulting
    from acts beyond its reasonable control.

    ARTICLE 9: ARBITRATION
    Any dispute arising out of or relating to this Agreement shall be resolved by
    binding arbitration in accordance with the rules of the American Arbitration
    Association.

    ARTICLE 10: ASSIGNMENT
    Neither party may assign this Agreement without the prior written consent of
    the other party.

    ARTICLE 11: NON-COMPETE
    During the Term and for one year thereafter, Contractor shall not engage in
    any business that competes with Client.

    ARTICLE 12: INSURANCE
    Contractor shall maintain comprehensive general liability insurance with
    limits of at least $1,000,000.

    ARTICLE 13: WARRANTY
    Contractor warrants that the Services will be performed in a professional and
    workmanlike manner.

    ARTICLE 14: SEVERABILITY
    If any provision of this Agreement is held to be invalid, the remaining
    provisions shall continue in full force and effect.

    ARTICLE 15: ENTIRE AGREEMENT
    This Agreement constitutes the entire understanding between the parties.
    """


def main():
    print("=" * 60)
    print("CONTRACT INTELLIGENCE PIPELINE TEST")
    print("=" * 60)

    # 1. Generate the contract text
    contract_text = generate_sample_contract()
    print("\n📄 Generated contract (first 300 chars):")
    print(contract_text[:300] + "...\n")

    # 2. Run clause segmentation + classification
    print("🔍 Running clause segmentation & classification...")
    clause_result = classify_contract(contract_text)
    print(f"   ✅ Found {clause_result['summary']['total_clauses']} clauses")

    # 3. Run risk assessment
    print("\n📊 Running risk assessment...")
    risk = score_contract(clause_result)

    # 4. Display the full result nicely
    print("\n" + "=" * 60)
    print("🧾 FINAL RISK ASSESSMENT")
    print("=" * 60)

    print(f"\n📈 Risk Score: {risk['risk_score']} / 100")
    print(f"🏷️  Risk Level: {risk['risk_level'].upper()}")

    print("\n📌 Risk Breakdown (weighted by confidence):")
    for item in risk['risk_breakdown']:
        clause_name = item['clause'].replace('_', ' ').title()
        print(f"   • {clause_name:25} | weight: {item['weight']:2} | "
              f"conf: {item['confidence']:.2f} | contrib: {item['contribution']:.2f}")

    if risk['missing_clauses']:
        print("\n⚠️  MISSING MANDATORY CLAUSES:")
        for clause in risk['missing_clauses']:
            print(f"   • {clause.replace('_', ' ').title()}")

    if risk['recommendations']:
        print("\n💡 RECOMMENDATIONS:")
        for rec in risk['recommendations']:
            print(f"   ✓ {rec}")

    if risk['unknown_clauses_count'] > 0:
        print(f"\n❓ Unknown clauses detected: {risk['unknown_clauses_count']}")

    # Optional: Save the full JSON output to a file
    with open("risk_output.json", "w") as f:
        json.dump(risk, f, indent=2)
    print("\n✅ Full risk output saved to 'risk_output.json'")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()