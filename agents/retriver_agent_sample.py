# sample_usage.py
from libraries import *
from retriever_agent import RetrieverAgent

def main():
    # Initialize the RetrieverAgent
    retriever = RetrieverAgent()
    
    # Sample 1: Basic Legal Document Search
    print("\n=== Sample 1: Basic Legal Document Search ===")
    documents = retriever.search_legal_documents(
        query="non-disclosure agreement technology sector",
        jurisdiction="California",
        doc_type="template",
        max_results=5
    )
    print(f"Found {len(documents)} relevant documents")
    
    # Sample 2: Search with Date Range
    print("\n=== Sample 2: Search with Date Range ===")
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 1, 1)
    recent_documents = retriever.search_legal_documents(
        query="data privacy regulations",
        jurisdiction="EU",
        doc_type="regulation",
        date_range=(start_date, end_date),
        max_results=3
    )
    print(f"Found {len(recent_documents)} recent documents")
    
    # Sample 3: Retrieve Standard Clauses
    print("\n=== Sample 3: Retrieve Standard Clauses ===")
    clauses = retriever.retrieve_standard_clauses(
        clause_type="confidentiality",
        jurisdiction="US",
        industry="technology"
    )
    print(f"Found {len(clauses)} standard clauses")
    
    # Sample 4: Query External Legal Database
    print("\n=== Sample 4: Query External Legal Database ===")
    westlaw_results = retriever.query_external_api(
        api_name="westlaw",
        query_params={
            "search_term": "intellectual property litigation",
            "jurisdiction": "federal",
            "date_range": "last_5_years"
        }
    )
    print("Retrieved results from Westlaw")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")

# Example with more detailed processing
def process_contract_requirements(contract_type: str, industry: str, jurisdiction: str):
    """
    Process specific contract requirements using the RetrieverAgent.
    """
    retriever = RetrieverAgent()
    
    try:
        # 1. Get relevant templates
        templates = retriever.search_legal_documents(
            query=f"{contract_type} template {industry}",
            jurisdiction=jurisdiction,
            doc_type="template",
            max_results=3
        )
        
        # 2. Get standard clauses
        standard_clauses = retriever.retrieve_standard_clauses(
            clause_type=contract_type,
            jurisdiction=jurisdiction,
            industry=industry
        )
        
        # 3. Get recent legal precedents
        precedents = retriever.search_legal_documents(
            query=f"{contract_type} precedent cases {industry}",
            jurisdiction=jurisdiction,
            doc_type="case_law",
            date_range=(
                datetime(2019, 1, 1),
                datetime.now()
            ),
            max_results=5
        )
        
        # 4. Get regulatory requirements
        regulations = retriever.query_external_api(
            api_name="lexisnexis",
            query_params={
                "document_type": "regulation",
                "industry": industry,
                "jurisdiction": jurisdiction,
                "topic": contract_type
            }
        )
        
        return {
            "templates": templates,
            "standard_clauses": standard_clauses,
            "precedents": precedents,
            "regulations": regulations
        }
        
    except Exception as e:
        print(f"Error processing contract requirements: {str(e)}")
        raise

# Example usage for specific contract type
def generate_employment_contract():
    """
    Example of using RetrieverAgent for employment contract generation.
    """
    try:
        requirements = process_contract_requirements(
            contract_type="employment",
            industry="technology",
            jurisdiction="California"
        )
        
        print("\n=== Employment Contract Requirements ===")
        print(f"Templates found: {len(requirements['templates'])}")
        print(f"Standard clauses: {len(requirements['standard_clauses'])}")
        print(f"Relevant precedents: {len(requirements['precedents'])}")
        print(f"Regulatory requirements retrieved: {bool(requirements['regulations'])}")
        
        return requirements
        
    except Exception as e:
        print(f"Error generating employment contract: {str(e)}")
        raise

# Run specific example
if __name__ == "__main__":
    try:
        print("\nGenerating Employment Contract Requirements...")
        result = generate_employment_contract()
        print("\nProcess completed successfully!")
        
    except Exception as e:
        print(f"\nError in contract generation process: {str(e)}")