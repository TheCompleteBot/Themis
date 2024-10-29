import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from openai import OpenAI
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

from .contract_analyzing_agent import ContractAnalyzer
from .contract_formatting_agent import ContractFormatter

class UserInterfaceAgent:
    """Main class for handling contract generation and user interaction"""
    
    def __init__(self):
        """Initialize the UserInterfaceAgent with necessary components"""
        self.client = OpenAI()
        self.analyzer = ContractAnalyzer(self.client)
        self.formatter = ContractFormatter()
        self.logger = logging.getLogger(__name__)
        self.output_file = "contract.pdf"
        self.line_separator = "-" * 80
        self.valid_contract_types = ['employment', 'service', 'lease', 'nda']

    def collect_user_inputs(self) -> Dict:
        """Collect contract information from user with validation"""
        print("\nWelcome to the AI Legal Contract Generator!")
        print(self.line_separator)
        print("Please provide the following information:\n")

        try:
            requirements = {}
            
            # Basic Information with validation
            while True:
                contract_type = input("Enter contract type (employment/service/lease/nda): ").strip().lower()
                if contract_type in self.valid_contract_types:
                    requirements['contract_type'] = contract_type
                    break
                print(f"Invalid contract type. Please choose from: {', '.join(self.valid_contract_types)}")
            
            requirements['party1'] = input("Enter first party name: ").strip()
            while not requirements['party1']:
                print("First party name cannot be empty.")
                requirements['party1'] = input("Enter first party name: ").strip()
            
            requirements['party2'] = input("Enter second party name: ").strip()
            while not requirements['party2']:
                print("Second party name cannot be empty.")
                requirements['party2'] = input("Enter second party name: ").strip()
            
            requirements['jurisdiction'] = input("Enter jurisdiction (e.g., Karnataka, India): ").strip()
            while not requirements['jurisdiction']:
                print("Jurisdiction cannot be empty.")
                requirements['jurisdiction'] = input("Enter jurisdiction (e.g., Karnataka, India): ").strip()
            
            # Collect additional jurisdictions
            additional_jurisdictions = []
            print("\nEnter additional jurisdictions (press Enter when done):")
            while True:
                jurisdiction = input("Additional jurisdiction (or press Enter to skip): ").strip()
                if not jurisdiction:
                    break
                additional_jurisdictions.append(jurisdiction)
            requirements['additional_jurisdictions'] = additional_jurisdictions

            # Contract-specific details
            requirements['details'] = self._collect_contract_specific_details(requirements['contract_type'])
            
            # Additional Information
            requirements['additional_info'] = input("\nAny additional clauses or special requirements? (Press Enter to skip): ").strip()

            # Display summary and confirm
            if self._display_input_summary(requirements):
                return requirements
            else:
                return self.collect_user_inputs()  # Restart if not confirmed

        except Exception as e:
            self.logger.error(f"Error collecting user inputs: {str(e)}")
            raise

    def _collect_contract_specific_details(self, contract_type: str) -> Dict:
        """Collect details specific to contract type with validation"""
        details = {}
        print("\nPlease provide contract-specific details:")

        def validate_date(date_str: str) -> bool:
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return True
            except ValueError:
                return False

        def validate_amount(amount: str) -> bool:
            try:
                return float(amount.replace(',', '').replace('INR', '').strip()) > 0
            except ValueError:
                return False

        if contract_type == 'employment':
            details['position'] = input("Position: ").strip()
            while not details['position']:
                print("Position cannot be empty.")
                details['position'] = input("Position: ").strip()

            details['salary'] = input("Salary (e.g., INR 50,000): ").strip()
            while not validate_amount(details['salary']):
                print("Please enter a valid salary amount.")
                details['salary'] = input("Salary (e.g., INR 50,000): ").strip()

            details['start_date'] = input("Start Date (YYYY-MM-DD): ").strip()
            while not validate_date(details['start_date']):
                print("Please enter a valid date in YYYY-MM-DD format.")
                details['start_date'] = input("Start Date (YYYY-MM-DD): ").strip()

            details['working_hours'] = input("Working Hours (e.g., 9:00 AM to 6:00 PM): ").strip()
            details['probation_period'] = input("Probation Period (e.g., 3 months): ").strip()
            details['notice_period'] = input("Notice Period (e.g., 30 days): ").strip()
            
            # Additional employment benefits
            print("\nAdditional Benefits:")
            details['benefits'] = {
                'health_insurance': input("Health Insurance Coverage (e.g., INR 5,00,000): ").strip(),
                'leaves': input("Annual Leaves (e.g., 24 days): ").strip(),
                'flexible_hours': input("Flexible Hours Policy (yes/no): ").strip().lower() == 'yes'
            }
        
        elif contract_type == 'service':
            details['service_description'] = input("Service Description: ").strip()
            while not details['service_description']:
                print("Service description cannot be empty.")
                details['service_description'] = input("Service Description: ").strip()

            details['duration'] = input("Service Duration (e.g., 12 months): ").strip()
            details['payment_terms'] = input("Payment Terms: ").strip()
            details['deliverables'] = input("Deliverables: ").strip()
            
        elif contract_type == 'lease':
            details['property_address'] = input("Property Address: ").strip()
            while not details['property_address']:
                print("Property address cannot be empty.")
                details['property_address'] = input("Property Address: ").strip()

            details['lease_term'] = input("Lease Term (e.g., 11 months): ").strip()
            details['monthly_rent'] = input("Monthly Rent: ").strip()
            while not validate_amount(details['monthly_rent']):
                print("Please enter a valid rent amount.")
                details['monthly_rent'] = input("Monthly Rent: ").strip()

            details['security_deposit'] = input("Security Deposit: ").strip()
            details['maintenance_terms'] = input("Maintenance Terms: ").strip()
            
        elif contract_type == 'nda':
            details['confidential_info'] = input("Type of Confidential Information: ").strip()
            while not details['confidential_info']:
                print("Confidential information type cannot be empty.")
                details['confidential_info'] = input("Type of Confidential Information: ").strip()

            details['duration'] = input("Duration of Confidentiality: ").strip()
            details['purpose'] = input("Purpose of Disclosure: ").strip()
            details['restrictions'] = input("Special Restrictions: ").strip()

        return details

    def display_final_contract(self, contract: str) -> None:
        """Display the final contract and save as PDF"""
        try:
            # Print the contract content
            self._print_contract(contract)
            
            # Generate and save PDF version
            self._save_pdf_version(contract)
            
            # Offer section review
            self._offer_section_review(contract)
            
        except Exception as e:
            self.logger.error(f"Error displaying final contract: {str(e)}")
            raise

    def _save_pdf_version(self, contract: str) -> None:
        """Generate and save PDF version of the contract"""
        try:
            # Analyze contract structure
            analysis = self.analyzer.analyze_contract(contract)
            template = self.analyzer.generate_template(analysis)
            
            # Setup formatting
            self.formatter.setup_styles(
                analysis['contract_type'],
                analysis.get('formatting_requirements', {})
            )
            
            # Create PDF
            self._create_pdf(contract, template, analysis)
            
        except Exception as e:
            self.logger.error(f"Error saving PDF version: {str(e)}")
            print("\nWarning: Could not generate PDF version. Displaying text-only version.")

    def _print_contract(self, contract: str) -> None:
        """Print contract content to console"""
        print("\nFINAL CONTRACT")
        print(self.line_separator)
        print(contract)
        print(self.line_separator)

    def _create_pdf(self, content: str, template: Dict, analysis: Dict) -> None:
        """Create formatted PDF document"""
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(self.output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Create PDF document
            doc = SimpleDocTemplate(
                self.output_file,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            story = []
            
            # Process sections
            sections = self._process_content(content)
            
            for section in sections:
                style = self._get_style_for_section(section)
                story.append(Paragraph(section['content'], style))
                
                if section.get('spacing'):
                    story.append(Spacer(1, section['spacing']))

            # Add metadata
            self._add_metadata(story, analysis['contract_type'])
            
            # Build PDF
            doc.build(story)
            print(f"\nContract has been saved as {self.output_file}")

        except Exception as e:
            self.logger.error(f"Error creating PDF: {str(e)}")
            raise

    def _process_content(self, content: str) -> List[Dict]:
        """Process content into formatted sections"""
        sections = []
        current_section = None
        current_content = []

        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Handle section headers
            if line.startswith('**') and line.endswith('**'):
                if current_section and current_content:
                    sections.append(self._create_section(current_section, current_content))
                current_section = 'heading'
                current_content = [line]
            
            # Handle list items
            elif line.startswith('- '):
                if current_section != 'list':
                    if current_content:
                        sections.append(self._create_section(current_section, current_content))
                    current_section = 'list'
                    current_content = []
                current_content.append(line)
            
            # Handle normal text
            else:
                if current_section == 'list' and current_content:
                    sections.append(self._create_section(current_section, current_content))
                    current_section = 'text'
                    current_content = []
                current_content.append(line)

        # Add final section
        if current_content:
            sections.append(self._create_section(current_section, current_content))

        return sections

    def _create_section(self, section_type: str, content: List[str]) -> Dict:
        """Create a properly formatted section"""
        section = {
            'content': '\n'.join(content),
            'type': section_type,
            'spacing': 10
        }

        if section_type == 'heading':
            section.update({
                'type': 'section',
                'style': 'SectionHeading',
                'spacing': 15
            })
        elif section_type == 'list':
            section.update({
                'type': 'list',
                'style': 'ListItem',
                'spacing': 6
            })
        else:
            section.update({
                'type': 'content',
                'style': 'NormalText',
                'spacing': 10
            })

        return section

    def _get_style_for_section(self, section: Dict) -> ParagraphStyle:
        """Get appropriate style for section"""
        if 'style' in section:
            return self.formatter.styles[section['style']]
        
        style_mapping = {
            'title': 'ContractTitle',
            'section': 'SectionHeading',
            'subsection': 'SubsectionHeading',
            'content': 'NormalText',
            'list': 'ListItem',
            'signature': 'Signature'
        }
        return self.formatter.styles[style_mapping.get(section['type'], 'NormalText')]

    def _add_metadata(self, story: List, contract_type: str) -> None:
        """Add metadata to document"""
        story.append(Spacer(1, 20))
        story.append(Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.formatter.styles['NormalText']
        ))
        story.append(Paragraph(
            f"Document Type: {contract_type.title()} Contract",
            self.formatter.styles['NormalText']
        ))

    def _offer_section_review(self, contract: str) -> None:
        """Offer user the option to review specific sections"""
        while True:
            review = input("\nWould you like to review a specific section? (yes/no): ").strip().lower()
            if review == 'no':
                break
            elif review == 'yes':
                section = input("Enter the section name or keyword to search: ").strip()
                self._display_section(contract, section)
            else:
                print("Please enter 'yes' or 'no'.")

    def _display_section(self, contract: str, section: str) -> None:
        """Display a specific section of the contract"""
        print("\nRELEVANT SECTIONS")
        print(self.line_separator)
        
        found = False
        for paragraph in contract.split('\n\n'):
            if section.lower() in paragraph.lower():
                print(paragraph)
                print()
                found = True
        
        if not found:
            print(f"No sections found containing '{section}'")
        print(self.line_separator)

    def _display_input_summary(self, requirements: Dict) -> bool:
        """Display summary of collected inputs"""
        print("\nSUMMARY OF INPUTS")
        print(self.line_separator)
        
        for key, value in requirements.items():
            if key == 'details':
                print("\nContract Details:")
                for k, v in value.items():
                    if isinstance(v, dict):
                        print(f"\n  {k.replace('_', ' ').title()}:")
                        for sub_k, sub_v in v.items():
                            print(f"    {sub_k.replace('_', ' ').title()}: {sub_v}")
                    else:
                        print(f"  {k.replace('_', ' ').title()}: {v}")
            elif key == 'additional_jurisdictions':
                if value:
                    print("\nAdditional Jurisdictions:")
                    for jurisdiction in value:
                        print(f"  - {jurisdiction}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        print(self.line_separator)
        return self._confirm_inputs()

    def _confirm_inputs(self) -> bool:
        """Confirm inputs with user"""
        while True:
            confirm = input("\nAre these details correct? (yes/no): ").strip().lower()
            if confirm == 'yes':
                return True
            elif confirm == 'no':
                return False
            print("Please enter 'yes' or 'no'.")

    def generate_contract(self, requirements: Dict) -> None:
        """Generate and format contract based on requirements"""
        try:
            # Generate initial contract content
            content = self._generate_initial_content(requirements)
            
            # Analyze contract and generate template
            analysis = self.analyzer.analyze_contract(content)
            template = self.analyzer.generate_template(analysis)
            
            # Setup styles based on analysis
            self.formatter.setup_styles(
                analysis['contract_type'],
                analysis.get('formatting_requirements', {})
            )
            
            # Create formatted PDF
            self._create_pdf(content, template, analysis)
            
            # Display the final contract
            self.display_final_contract(content)
            
        except Exception as e:
            self.logger.error(f"Error generating contract: {str(e)}")
            raise

    def _generate_initial_content(self, requirements: Dict) -> str:
        """Generate initial contract content using AI"""
        try:
            # Prepare the prompt with clear instructions
            prompt = self._prepare_contract_prompt(requirements)

            # Generate content using OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a legal contract drafting expert. Create detailed, well-structured contracts with proper formatting, clear sections, and comprehensive terms."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=3000
            )

            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"Error generating initial content: {str(e)}")
            raise

    def _prepare_contract_prompt(self, requirements: Dict) -> str:
        """Prepare detailed prompt for contract generation"""
        prompt = f"""Create a detailed {requirements['contract_type']} contract with the following specifications:

1. Contract Type: {requirements['contract_type'].upper()}
2. Parties:
   - First Party: {requirements['party1']}
   - Second Party: {requirements['party2']}
3. Jurisdiction: {requirements['jurisdiction']}

4. Specific Details:
{json.dumps(requirements['details'], indent=4)}

5. Additional Information:
{requirements['additional_info'] if requirements['additional_info'] else 'N/A'}

6. Additional Jurisdictions:
{', '.join(requirements['additional_jurisdictions']) if requirements['additional_jurisdictions'] else 'N/A'}

Please create a comprehensive contract that:
1. Uses clear section headings marked with ** (e.g., **SECTION TITLE**)
2. Includes all necessary legal clauses and protections
3. Incorporates jurisdiction-specific requirements
4. Uses proper legal terminology and formatting
5. Includes all standard sections (definitions, terms, termination, etc.)
6. Properly formats lists with bullet points (-)
7. Includes signature blocks and date fields
8. Adds any necessary references or citations

Format the contract clearly with:
- Bold section headings
- Proper spacing between sections
- Clear numbering for clauses
- Proper indentation for subclauses
- Professional layout
"""
        return prompt

    def __del__(self):
        """Cleanup method"""
        try:
            self.client.close()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize and run
    agent = UserInterfaceAgent()
    try:
        requirements = agent.collect_user_inputs()
        if requirements:
            agent.generate_contract(requirements)
    except Exception as e:
        print(f"Error: {str(e)}")