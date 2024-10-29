from typing import List, Dict
import logging
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class RetrieverAgent:
    """
    Simplified retriever agent using InLegalBERT for legal document search.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Initialize InLegalBERT model and tokenizer
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = AutoTokenizer.from_pretrained('law-ai/InLegalBERT')
        self.model = AutoModel.from_pretrained('law-ai/InLegalBERT').to(self.device)
        self._load_legal_database()

    def search_legal_reference(self, user_inputs: Dict) -> List[Dict]:
        """
        Search for relevant legal references based on user inputs.
        
        Args:
            user_inputs (Dict): Dictionary containing:
                - contract_type: Type of contract
                - details: Specific requirements
                - jurisdiction: Legal jurisdiction
                
        Returns:
            List[Dict]: Relevant legal references
        """
        try:
            # Construct search query from user inputs
            query = self._construct_search_query(user_inputs)
            
            # Get query embedding
            query_embedding = self._get_embedding(query)
            
            # Get relevant references
            relevant_refs = self._find_relevant_references(
                query_embedding, 
                user_inputs['contract_type']
            )
            
            return relevant_refs

        except Exception as e:
            self.logger.error(f"Error in legal reference search: {str(e)}")
            return []

    def _construct_search_query(self, user_inputs: Dict) -> str:
        """Construct a search query from user inputs"""
        contract_type = user_inputs['contract_type']
        details = user_inputs.get('details', {})
        
        # Build query based on contract type
        if contract_type == 'employment':
            query = f"""
            Employment contract with position {details.get('position')}
            Salary: {details.get('salary')}
            Location: {details.get('location')}
            Working hours: {details.get('working_hours')}
            Jurisdiction: {user_inputs.get('jurisdiction')}
            """
        elif contract_type == 'nda':
            query = f"""
            Non-disclosure agreement
            Parties involved: {details.get('party1')} and {details.get('party2')}
            Jurisdiction: {user_inputs.get('jurisdiction')}
            Confidential information: {details.get('confidential_info')}
            """
        elif contract_type == 'service':
            query = f"""
            Service agreement for {details.get('service_type')}
            Service provider: {details.get('provider')}
            Service recipient: {details.get('recipient')}
            Jurisdiction: {user_inputs.get('jurisdiction')}
            """
        elif contract_type == 'lease':
            query = f"""
            Lease agreement for {details.get('property_type')}
            Landlord: {details.get('landlord')}
            Tenant: {details.get('tenant')}
            Duration: {details.get('duration')}
            Jurisdiction: {user_inputs.get('jurisdiction')}
            """
        else:
            query = f"{contract_type} contract in {user_inputs.get('jurisdiction')}"
            
        return query.strip()

    def _get_embedding(self, text: str) -> np.ndarray:
        """Get InLegalBERT embedding for text"""
        inputs = self.tokenizer(
            text,
            max_length=512,
            padding=True,
            truncation=True,
            return_tensors='pt'
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]
            
        return embedding

    def _find_relevant_references(self, query_embedding: np.ndarray, contract_type: str) -> List[Dict]:
        """Find relevant legal references"""
        relevant_refs = []
        
        # Filter references by contract type first
        type_refs = [ref for ref in self.legal_database if contract_type in ref['categories']]
        
        if not type_refs:
            return relevant_refs
            
        # Get embeddings for filtered references
        ref_embeddings = []
        for ref in type_refs:
            ref_text = f"{ref['title']} {ref['content']}"
            ref_embeddings.append(self._get_embedding(ref_text))
            
        # Calculate similarities
        similarities = cosine_similarity(
            query_embedding.reshape(1, -1),
            np.array(ref_embeddings)
        )[0]
        
        # Get top 5 most relevant references
        top_indices = np.argsort(similarities)[-5:][::-1]
        
        for idx in top_indices:
            if similarities[idx] > 0.3:  # Minimum relevance threshold
                ref = type_refs[idx].copy()
                ref['relevance_score'] = float(similarities[idx])
                relevant_refs.append(ref)
        
        return relevant_refs

    def _load_legal_database(self):
        """Load legal reference database with multiple contract types"""
        self.legal_database = [
            # Employment Contracts
            {
                'title': 'Employment Agreement Basics',
                'content': 'Employment agreements must specify position, compensation, working hours, and duties. Clear termination clauses and notice periods are required.',
                'source': 'Employment Act',
                'categories': ['employment']
            },
            {
                'title': 'Workplace Rights and Obligations',
                'content': 'Employees have the right to safe working conditions, fair compensation, and protection from discrimination. Employers must provide statutory benefits.',
                'source': 'Labor Rights Act',
                'categories': ['employment']
            },
            
            # NDAs
            {
                'title': 'Confidentiality Requirements',
                'content': 'NDAs must clearly define confidential information, specify duration of confidentiality, and outline permitted uses of information.',
                'source': 'Trade Secrets Protection Act',
                'categories': ['nda']
            },
            {
                'title': 'NDA Enforcement Guidelines',
                'content': 'Non-disclosure agreements must be reasonable in scope and duration. Overly restrictive NDAs may be unenforceable.',
                'source': 'Contract Law Handbook',
                'categories': ['nda']
            },
            
            # Service Agreements
            {
                'title': 'Service Contract Requirements',
                'content': 'Service agreements must specify scope of services, payment terms, delivery timeline, and quality standards.',
                'source': 'Contract Law',
                'categories': ['service']
            },
            {
                'title': 'Service Provider Obligations',
                'content': 'Service providers must deliver services professionally, maintain required licenses, and carry appropriate insurance.',
                'source': 'Professional Services Act',
                'categories': ['service']
            },
            
            # Lease Agreements
            {
                'title': 'Residential Lease Requirements',
                'content': 'Lease agreements must specify rent amount, payment schedule, security deposit terms, and maintenance responsibilities.',
                'source': 'Property Law',
                'categories': ['lease']
            },
            {
                'title': 'Tenant Rights and Obligations',
                'content': 'Tenants have rights to habitable premises and proper notice for entry. Maintenance and use restrictions must be clearly stated.',
                'source': 'Residential Tenancy Act',
                'categories': ['lease']
            }
        ]