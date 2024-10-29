from typing import Dict, List, TypedDict, Annotated, Sequence
from langgraph.graph import Graph, END
from typing import Union
import logging
from dotenv import load_dotenv
from openai import OpenAI

# Import agents
from agents.user_interface_agent import UserInterfaceAgent
from agents.retriever_agent import RetrieverAgent
from agents.drafting_agent import DraftingAgent
from agents.correction_agent import CorrectionAgent
from agents.jurisdiction_agent import JurisdictionCustomizationAgent

# Load environment variables
load_dotenv()

# Define state type
class ContractState(TypedDict):
    user_inputs: Dict
    legal_references: List[Dict]
    contract_draft: str
    corrected_draft: str
    final_contract: str
    error: str | None
    completed: bool

# Initialize agents
ui_agent = UserInterfaceAgent()
retriever_agent = RetrieverAgent()
drafting_agent = DraftingAgent()
correction_agent = CorrectionAgent()
jurisdiction_agent = JurisdictionCustomizationAgent()
logger = logging.getLogger(__name__)

# Define node functions
def collect_user_inputs(state: ContractState) -> Dict:
    """Collect user inputs node with hardcoded test data for Indian context"""
    try:
        logger.info("Collecting user inputs...")
        
        # Hardcoded test data for Employment Contract
        # test_inputs = {
        #     'contract_type': 'employment',
        #     'party1': 'TechnoBlade India Pvt. Ltd.',
        #     'party2': 'Aayush Sharma',
        #     'jurisdiction': 'Karnataka, India',
        #     'additional_jurisdictions': ['Maharashtra, India'],
        #     'details': {
        #         'position': 'Senior Software Engineer',
        #         'salary': 'INR 24,00,000 per annum',
        #         'start_date': '2024-05-01',
        #         'location': 'Bengaluru, Karnataka',
        #         'working_hours': '9:30 AM to 6:30 PM IST',
        #         'probation_period': '6 months',
        #         'notice_period': '90 days',
        #         # Additional India-specific details
        #         'pf_contribution': 'As per EPF Act',
        #         'gratuity': 'As per Gratuity Act',
        #         'leave_policy': '24 days paid leave per annum',
        #         'medical_insurance': 'Group medical coverage of INR 5,00,000',
        #         'flexible_benefits': {
        #             'hra': '40% of basic salary',
        #             'lta': 'INR 50,000 per annum',
        #             'meal_allowance': 'INR 2,200 per month',
        #             'telephone_allowance': 'INR 2,000 per month'
        #         }
        #     },
        #     'additional_info': """
        #     1. Flexible work hours with core hours 11 AM to 4 PM IST
        #     2. Work from home allowed 3 days per week
        #     3. Company laptop and internet allowance provided
        #     4. Annual performance bonus up to 20% of fixed compensation
        #     5. Employee stock options as per company ESOP policy
        #     6. Professional development allowance of INR 50,000 per annum
        #     """,
        #     'statutory_compliance': {
        #         'epf': 'Employees Provident Fund',
        #         'esi': 'Employees State Insurance (if applicable)',
        #         'professional_tax': 'As per Karnataka Professional Tax Act',
        #         'income_tax': 'TDS as per Income Tax Act, 1961'
        #     }
        # }

# Test input data for NDA Contract in Indian context
        test_inputs = {
            'contract_type': 'nda',
            'party1': 'TechVista Solutions Private Limited',  # Disclosing Party
            'party2': 'InnoServe Consulting LLP',            # Receiving Party
            'jurisdiction': 'Maharashtra, India',
            'additional_jurisdictions': ['Karnataka, India', 'Delhi, India'],
            'details': {
                'confidential_info': """
                    1. Technical Information:
                    - Software source code and architecture
                    - System designs and flowcharts
                    - Technical specifications
                    - Research and development data
                    - Testing methodologies and results
                    
                    2. Business Information:
                    - Client lists and data
                    - Pricing strategies
                    - Marketing plans
                    - Financial projections
                    - Business processes
                    
                    3. Intellectual Property:
                    - Patents (filed and unfiled)
                    - Trade secrets
                    - Proprietary algorithms
                    - Database designs
                """,
                'purpose': 'For the evaluation and potential collaboration on Project Nexus - AI-driven Analytics Platform',
                'duration': '5 years from the Effective Date',
                'survival_period': '3 years after termination',
                'restrictions': {
                    'data_handling': 'Confidential Information must be stored in encrypted format with AES-256 encryption',
                    'access_control': 'Need-to-know basis with documented access logs',
                    'transmission': 'Only through secure channels with end-to-end encryption',
                    'copies': 'Limited to essential copies only, with digital watermarking'
                },
                'return_requirements': {
                    'timeframe': '15 days from termination/request',
                    'format': 'All physical and digital copies, including derivatives',
                    'certification': 'Written certification of complete return/destruction required'
                },
                'security_measures': {
                    'physical': 'Secure access-controlled premises',
                    'digital': 'Multi-factor authentication, encryption, audit logs',
                    'personnel': 'Background checks and individual NDAs required'
                }
            },
            'additional_info': """
            1. Compliance Requirements:
            - IT Act, 2000 compliance
            - SPDI Rules, 2011 compliance
            - Data localization requirements
            - Industry-specific regulatory compliance
            
            2. Specific Exclusions:
            - Information already in public domain
            - Independently developed information
            - Information received from third parties without restriction
            - Information required to be disclosed by law
            
            3. Special Conditions:
            - Immediate notification requirement for any breach
            - Quarterly compliance reports
            - Right to audit security measures
            - Specific requirements for cross-border data transfer
            """,
            'statutory_compliance': {
                'it_act': 'Information Technology Act, 2000',
                'spdi_rules': 'Sensitive Personal Data Information Rules, 2011',
                'companies_act': 'Companies Act, 2013 compliance',
                'contract_act': 'Indian Contract Act, 1872'
            },
            'dispute_resolution': {
                'governing_law': 'Laws of India',
                'jurisdiction': 'Courts of Mumbai',
                'arbitration': {
                    'seat': 'Mumbai',
                    'rules': 'Indian Arbitration and Conciliation Act, 1996',
                    'language': 'English',
                    'arbitrators': 'Single arbitrator mutually appointed'
                }
            },
            'remedies': {
                'injunctive_relief': 'Right to seek immediate injunctive relief',
                'damages': 'Right to claim actual and exemplary damages',
                'specific_performance': 'Right to seek specific performance'
            }
        }  
        logger.info("User inputs collected.")
        state["user_inputs"] = test_inputs
        return state
    except Exception as e:
        logger.error(f"Error collecting user inputs: {str(e)}")
        state["error"] = str(e)
        return state
def retrieve_legal_references(state: ContractState) -> Dict:
    """Retrieve legal references node with debugging"""
    try:
        logger.info("Retrieving legal references...")
        
        # Get relevant legal references
        legal_references = retriever_agent.search_legal_reference(
            state["user_inputs"]
        )
        
        # Debug print the retrieved references
        logger.info("\n=== Retrieved Legal References ===")
        for i, ref in enumerate(legal_references, 1):
            logger.info(f"\nReference {i}:")
            logger.info(f"Source: {ref['source']}")
            logger.info(f"Content: {ref['content']}")
            if 'relevance_score' in ref:
                logger.info(f"Relevance Score: {ref['relevance_score']:.2f}")
            logger.info("-" * 50)
        
        state["legal_references"] = legal_references
        return state
        
    except Exception as e:
        logger.error(f"Error retrieving legal references: {str(e)}")
        state["error"] = str(e)
        return state


def generate_initial_draft(state: ContractState) -> Dict:
    """Generate initial contract draft node"""
    try:
        logger.info("Generating initial draft...")
        contract = drafting_agent.create_initial_draft(
            contract_type=state["user_inputs"]["contract_type"],
            requirements=state["user_inputs"],  # Pass the entire user_inputs dict
            legal_refs=state["legal_references"]
        )
        logger.info("Initial draft generated.")
        state["contract_draft"] = contract
        return state
    except Exception as e:
        logger.error(f"Error generating draft: {str(e)}")
        state["error"] = str(e)
        return state
def correct_draft(state: ContractState) -> Dict:
    """Correct contract draft node"""
    try:
        logger.info("Correcting the draft...")
        corrected = correction_agent.correct_draft(state["contract_draft"])
        logger.info("Draft corrected.")
        state["corrected_draft"] = corrected
        return state
    except Exception as e:
        logger.error(f"Error correcting draft: {str(e)}")
        state["error"] = str(e)
        return state

def customize_jurisdiction(state: ContractState) -> Dict:
    """Customize contract for jurisdiction node"""
    try:
        logger.info("Customizing draft for jurisdiction...")
        contract_dict = {
            'content': state["corrected_draft"],
            'metadata': {}
        }
        
        customized = jurisdiction_agent.customize_for_jurisdiction(
            contract_dict,
            state["user_inputs"].get('jurisdiction', 'Default Jurisdiction'),
            state["user_inputs"].get('additional_jurisdictions', []),
            requirements={'translate': False}
        )
        
        final_contract = customized['content'] if isinstance(customized, dict) else customized
        logger.info("Draft customized for jurisdiction.")
        state["final_contract"] = final_contract
        return state
    except Exception as e:
        logger.error(f"Error customizing for jurisdiction: {str(e)}")
        state["error"] = str(e)
        return state

def present_contract(state: ContractState) -> Dict:
    """Present final contract node"""
    try:
        # Display and save contract
        ui_agent.display_final_contract(state["final_contract"])
        logger.info("Contract generation and saving completed.")
        state["completed"] = True
        return state
    except Exception as e:
        logger.error(f"Error presenting contract: {str(e)}")
        state["error"] = str(e)
        return state
def should_continue(state: ContractState) -> Union[str, Sequence[str]]:
    """Determine if the workflow should continue or end"""
    if state.get("error"):
        return END
    return "continue"

# Create the workflow graph
def create_contract_graph() -> Graph:
    """Create the contract generation workflow graph"""
    
    # Create the graph
    workflow = Graph()
    
    # Add nodes to the graph
    workflow.add_node("collect_inputs", collect_user_inputs)
    workflow.add_node("retrieve_references", retrieve_legal_references)
    workflow.add_node("generate_draft", generate_initial_draft)
    workflow.add_node("correct_draft", correct_draft)
    workflow.add_node("customize_jurisdiction", customize_jurisdiction)
    workflow.add_node("present_contract", present_contract)
    
    # Set the entry point
    workflow.set_entry_point("collect_inputs")
    
    # Add conditional edges for each node
    workflow.add_conditional_edges(
        "collect_inputs",
        should_continue,
        {
            "continue": "retrieve_references",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "retrieve_references",
        should_continue,
        {
            "continue": "generate_draft",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "generate_draft",
        should_continue,
        {
            "continue": "correct_draft",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "correct_draft",
        should_continue,
        {
            "continue": "customize_jurisdiction",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "customize_jurisdiction",
        should_continue,
        {
            "continue": "present_contract",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "present_contract",
        should_continue,
        {
            "continue": END,
            END: END
        }
    )
    
    return workflow.compile()
# Main execution
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create the workflow
        workflow = create_contract_graph()
        
        # Initialize state
        initial_state = ContractState(
            user_inputs={},
            legal_references=[],
            contract_draft="",
            corrected_draft="",
            final_contract="",
            error=None,
            completed=False
        )
        
        # Execute the workflow
        final_state = workflow.invoke(initial_state)
        
        if final_state.get("error"):
            logger.error(f"Workflow error: {final_state['error']}")
        elif final_state.get("completed"):
            logger.info("Contract generation workflow completed successfully!")
            
    except Exception as e:
        logger.error(f"Error in workflow execution: {str(e)}")