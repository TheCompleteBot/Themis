from typing import List, Dict
import logging
from datetime import datetime
from openai import OpenAI


class DraftingAgent:
    """Enhanced drafting agent using GPT-3.5-turbo with reference tracking"""
    
    # Define templates as a class variable
    TEMPLATES = {
        'employment': """
1. POSITION AND DUTIES
2. COMPENSATION AND BENEFITS
3. WORKING HOURS AND LOCATION
4. PROBATION AND CONFIRMATION
5. LEAVE POLICY
6. STATUTORY BENEFITS
7. TERMINATION
8. CONFIDENTIALITY
9. INTELLECTUAL PROPERTY
10. DISPUTE RESOLUTION
""",
        'nda': """
1. PARTIES AND PURPOSE
2. DEFINITION OF CONFIDENTIAL INFORMATION
3. OBLIGATIONS OF RECEIVING PARTY
4. EXCLUSIONS FROM CONFIDENTIAL INFORMATION
5. TERM AND TERMINATION
6. RETURN OF CONFIDENTIAL INFORMATION
7. REMEDIES
8. GENERAL PROVISIONS
""",
        'service': """
1. SCOPE OF SERVICES
2. PAYMENT TERMS
3. SERVICE STANDARDS
4. TERM AND TERMINATION
5. INTELLECTUAL PROPERTY
6. CONFIDENTIALITY
7. WARRANTIES AND REPRESENTATIONS
8. LIMITATION OF LIABILITY
9. GENERAL PROVISIONS
""",
        'lease': """
1. PROPERTY DETAILS
2. TERM AND RENT
3. SECURITY DEPOSIT
4. UTILITIES AND MAINTENANCE
5. USE OF PROPERTY
6. TENANT OBLIGATIONS
7. LANDLORD OBLIGATIONS
8. TERMINATION
9. GENERAL PROVISIONS
"""
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI()
        self.references_used = []
        self.templates = self.TEMPLATES

    def _format_requirements(self, requirements: Dict) -> str:
        """Format requirements into a structured string for the AI prompt"""
        try:
            formatted = []
            details = requirements.get('details', {})
            
            # Format basic information
            formatted.append("BASIC INFORMATION:")
            formatted.append(f"Contract Type: {requirements.get('contract_type', 'Not specified')}")
            formatted.append(f"Employer: {requirements.get('party1', 'Not specified')}")
            formatted.append(f"Employee: {requirements.get('party2', 'Not specified')}")
            formatted.append(f"Jurisdiction: {requirements.get('jurisdiction', 'Not specified')}")
            
            # Format employment details
            if details:
                formatted.append("\nEMPLOYMENT DETAILS:")
                for key, value in details.items():
                    if isinstance(value, dict):
                        # Handle nested dictionaries (like benefits)
                        formatted.append(f"\n{key.replace('_', ' ').title()}:")
                        for sub_key, sub_value in value.items():
                            formatted.append(f"  - {sub_key.replace('_', ' ').title()}: {sub_value}")
                    else:
                        formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
            
            # Format statutory compliance
            if requirements.get('statutory_compliance'):
                formatted.append("\nSTATUTORY COMPLIANCE:")
                for key, value in requirements['statutory_compliance'].items():
                    formatted.append(f"- {key.upper()}: {value}")
            
            # Format additional information
            if requirements.get('additional_info'):
                formatted.append("\nADDITIONAL INFORMATION:")
                formatted.append(requirements['additional_info'])
            
            return "\n".join(formatted)
            
        except Exception as e:
            self.logger.error(f"Error formatting requirements: {str(e)}")
            raise

    def create_initial_draft(self, contract_type: str, requirements: Dict, legal_refs: List[Dict]) -> str:
        """Create initial contract draft with reference tracking"""
        try:
            # Reset references tracking
            self.references_used = []
            
            # Debug print incoming references
            self.logger.info("\n=== Available Legal References ===")
            for i, ref in enumerate(legal_refs, 1):
                self.logger.info(f"\nReference {i}:")
                self.logger.info(f"Source: {ref.get('source', 'Unknown')}")
                self.logger.info(f"Content: {ref.get('content', 'No content')}")
            self.logger.info("=" * 50)
            
            # Check if template exists
            if contract_type not in self.templates:
                raise ValueError(f"No template found for contract type: {contract_type}")
            
            # Generate draft with GPT-3.5
            draft = self._generate_draft_with_ai(requirements, legal_refs)
            
            # Add references section
            final_draft = self._add_references_section(draft)
            
            # Debug print used references
            self.logger.info("\n=== References Used in Draft ===")
            for i, ref in enumerate(self.references_used, 1):
                self.logger.info(f"\nReference {i}:")
                self.logger.info(f"Source: {ref['source']}")
                self.logger.info(f"Used in sections: {', '.join(ref['sections'])}")
            self.logger.info("=" * 50)
            
            return final_draft
            
        except Exception as e:
            self.logger.error(f"Error creating draft: {str(e)}")
            raise

    def _generate_draft_with_ai(self, requirements: Dict, legal_refs: List[Dict]) -> str:
        """Generate contract draft using GPT-3.5-turbo with explicit reference tracking"""
        try:
            # Format all legal references
            legal_context = []
            for i, ref in enumerate(legal_refs, 1):
                legal_context.append(f"Reference {i}:")
                legal_context.append(f"Source: {ref['source']}")
                legal_context.append(f"Content: {ref['content']}")
                legal_context.append("-" * 30)
            
            legal_context_str = "\n".join(legal_context)
            
            # Format requirements
            formatted_requirements = self._format_requirements(requirements)
            
            # Create the prompt
            prompt = f"""You are drafting an Indian legal contract with the following details:

REQUIREMENTS:
{formatted_requirements}

LEGAL REFERENCES:
{legal_context_str}

Please create a comprehensive contract that:
1. Follows Indian legal standards and regulations
2. Incorporates all relevant legal references
3. Marks references used with [Ref X] at the end of relevant sections
4. Uses clear, professional language
5. Includes all statutory requirements
6. Protects both parties' interests

After each major section, please indicate which references were used by adding:
"[References used: Ref X, Ref Y]"

Generate the contract now:"""

            # Call GPT-3.5-turbo
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an Indian legal expert specializing in contract law."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            self.logger.error(f"Error in AI draft generation: {str(e)}")
            raise

    def _track_references_used(self, draft: str, legal_refs: List[Dict]) -> None:
        """Enhanced reference tracking"""
        self.references_used = []
        sections = draft.split('\n\n')
        
        for i, ref in enumerate(legal_refs, 1):
            ref_marker = f"[Ref {i}]"
            found_sections = []
            
            for section in sections:
                if ref_marker in section:
                    # Extract section title
                    lines = section.split('\n')
                    if lines:
                        title = lines[0].strip()
                        if title and title not in found_sections:
                            found_sections.append(title)
            
            if found_sections:
                self.references_used.append({
                    'source': ref['source'],
                    'content': ref['content'],
                    'sections': found_sections
                })

    def _add_references_section(self, draft: str) -> str:
        """Add detailed references section"""
        if not self.references_used:
            return draft
            
        references_section = "\n\nLEGAL REFERENCES AND SOURCES\n"
        references_section += "=" * 50 + "\n\n"
        references_section += "The following legal references were used in drafting this contract:\n\n"
        
        for i, ref in enumerate(self.references_used, 1):
            references_section += f"Reference {i}:\n"
            references_section += f"Source: {ref['source']}\n"
            references_section += "Used in sections:\n"
            for section in ref['sections']:
                references_section += f"  • {section}\n"
            references_section += f"Content: {ref['content']}\n"
            references_section += "-" * 40 + "\n\n"
            
        return draft + references_section