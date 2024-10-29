# sample_usage.py
from libraries import *
from retriever_agent import RetrieverAgent
from drafting_agent import DraftingAgent

def create_nda_contract():
    """
    Example: Creating a Non-Disclosure Agreement (NDA)
    """
    # Initialize agents
    retriever = RetrieverAgent()
    drafter = DraftingAgent()

    # 1. Get template and clauses using RetrieverAgent
    template_data = retriever.search_legal_documents(
        query="non disclosure agreement template",
        jurisdiction="California",
        doc_type="template",
        max_results=1
    )[0]

    standard_clauses = retriever.retrieve_standard_clauses(
        clause_type="nda",
        jurisdiction="California",
        industry="technology"
    )

    # 2. Define user requirements
    user_requirements = {
        'parties': [
            {
                'name': 'TechCorp Inc.',
                'type': 'Disclosing Party',
                'address': '123 Tech Street, San Francisco, CA 94105',
                'state_of_incorporation': 'Delaware'
            },
            {
                'name': 'Innovative Solutions LLC',
                'type': 'Receiving Party',
                'address': '456 Innovation Ave, San Jose, CA 95113',
                'state_of_incorporation': 'California'
            }
        ],
        'effective_date': '2024-02-01',
        'term': {
            'duration': '2 years',
            'automatic_renewal': True,
            'renewal_period': '1 year'
        },
        'special_terms': [
            {
                'heading': 'Technical Information Protection',
                'content': 'Special handling of source code and technical specifications'
            },
            {
                'heading': 'Return of Materials',
                'content': 'Return or destruction of confidential materials within 30 days'
            }
        ]
    }

    # 3. Generate contract draft
    contract = drafter.generate_contract_draft(
        contract_type="nda",
        template_data=template_data,
        user_requirements=user_requirements,
        clauses=standard_clauses
    )

    print("\n=== NDA Contract Generated ===")
    print(f"Version: {contract['metadata']['version']}")
    print(f"Created: {contract['metadata']['created_at']}")
    print("\nContent Preview:")
    print(contract['content'][:500] + "...\n")

    return contract

def create_employment_contract():
    """
    Example: Creating an Employment Contract
    """
    retriever = RetrieverAgent()
    drafter = DraftingAgent()

    # 1. Retrieve necessary templates and clauses
    template_data = retriever.search_legal_documents(
        query="employment agreement template technology sector",
        jurisdiction="California",
        doc_type="template",
        max_results=1
    )[0]

    standard_clauses = retriever.retrieve_standard_clauses(
        clause_type="employment",
        jurisdiction="California",
        industry="technology"
    )

    # 2. Define employment-specific requirements
    user_requirements = {
        'parties': [
            {
                'name': 'TechCorp Inc.',
                'type': 'Employer',
                'address': '123 Tech Street, San Francisco, CA 94105'
            },
            {
                'name': 'John Doe',
                'type': 'Employee',
                'address': '789 Resident Lane, San Francisco, CA 94110'
            }
        ],
        'effective_date': '2024-03-01',
        'term': {
            'type': 'at-will'
        },
        'compensation': {
            'base_salary': '150000',
            'currency': 'USD',
            'payment_frequency': 'bi-weekly',
            'bonus': {
                'type': 'performance',
                'target_percentage': 15
            }
        },
        'benefits': {
            'health_insurance': True,
            'dental_insurance': True,
            'vision_insurance': True,
            '401k': {
                'available': True,
                'company_match': '4'
            }
        },
        'special_terms': [
            {
                'heading': 'Remote Work Policy',
                'content': 'Hybrid work arrangement with 2 days in office'
            },
            {
                'heading': 'Stock Options',
                'content': '10000 ISO units with 4-year vesting'
            }
        ]
    }

    # 3. Generate contract
    contract = drafter.generate_contract_draft(
        contract_type="employment",
        template_data=template_data,
        user_requirements=user_requirements,
        clauses=standard_clauses
    )

    print("\n=== Employment Contract Generated ===")
    print(f"Version: {contract['metadata']['version']}")
    print(f"Created: {contract['metadata']['created_at']}")
    
    # 4. Demonstrate version control
    # Make some modifications
    user_requirements['compensation']['base_salary'] = '160000'
    updated_contract = drafter.generate_contract_draft(
        contract_type="employment",
        template_data=template_data,
        user_requirements=user_requirements,
        clauses=standard_clauses
    )

    print("\n=== Version History ===")
    history = drafter.get_version_history()
    for version in history:
        print(f"Version {version['version']}: {version['timestamp']}")

    # 5. Rollback demonstration
    previous_version = drafter.rollback_to_version(1)
    print("\n=== Rolled Back to Version 1 ===")
    print(f"Base Salary in V1: {previous_version['sections']['terms'][2]['content']}")

    return contract

def main():
    try:
        print("\nGenerating NDA Contract...")
        nda_contract = create_nda_contract()
        
        print("\nGenerating Employment Contract...")
        employment_contract = create_employment_contract()
        
        print("\nAll contracts generated successfully!")
        
    except Exception as e:
        print(f"\nError in contract generation: {str(e)}")

if __name__ == "__main__":
    main()