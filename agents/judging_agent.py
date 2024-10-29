# agents/judging_agent.py
from libraries import *
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import sqlite3
import os

@dataclass
class ComplianceIssue:
    """Data structure for compliance issues in Indian context"""
    issue_id: str
    category: str  # 'legal', 'regulatory', 'procedural'
    description: str
    reference: str  # Reference to specific Indian law/regulation
    severity: str  # 'critical', 'major', 'minor'
    suggested_remedy: str

class JudgingAgent:
    """
    Modified Judging Agent for Indian legal compliance and enforcement checks.
    Focuses on Indian laws, regulations, and legal requirements.
    """
    def __init__(self, llm: OpenAI = None):
        self.logger = logging.getLogger(__name__)
        self.llm = llm or OpenAI(temperature=0.2)
        
        # Initialize local storage
        self.db_path = 'data/compliance_data.db'
        self._initialize_local_storage()
        
        # Load Indian legal requirements
        self._load_indian_legal_requirements()

    def evaluate_legal_compliance(
        self,
        contract: Dict,
        jurisdiction: str,
        contract_type: str
    ) -> Dict:
        """
        Evaluate contract for Indian legal compliance.
        
        Args:
            contract (Dict): Contract to evaluate
            jurisdiction (str): Indian jurisdiction (e.g., "Maharashtra")
            contract_type (str): Type of contract
            
        Returns:
            Dict: Compliance evaluation results
        """
        try:
            evaluation = {
                'timestamp': datetime.now().isoformat(),
                'contract_id': contract.get('id', ''),
                'jurisdiction': jurisdiction,
                'compliance_status': 'pending',
                'issues': [],
                'regulatory_checks': {},
                'enforceability': {},
                'stamp_duty': {},
                'registration': {},
                'recommendations': []
            }

            # 1. Check central laws compliance
            central_compliance = self._check_central_law_compliance(
                contract,
                contract_type
            )
            evaluation['issues'].extend(central_compliance)

            # 2. Check state-specific compliance
            state_compliance = self._check_state_compliance(
                contract,
                jurisdiction
            )
            evaluation['issues'].extend(state_compliance)

            # 3. Check stamp duty requirements
            evaluation['stamp_duty'] = self._check_stamp_duty_requirements(
                contract,
                jurisdiction,
                contract_type
            )

            # 4. Check registration requirements
            evaluation['registration'] = self._check_registration_requirements(
                contract,
                jurisdiction
            )

            # 5. Check enforceability
            evaluation['enforceability'] = self._assess_enforceability(
                contract,
                jurisdiction
            )

            # 6. Generate recommendations
            evaluation['recommendations'] = self._generate_recommendations(
                evaluation['issues'],
                evaluation['stamp_duty'],
                evaluation['registration']
            )

            # 7. Set overall compliance status
            evaluation['compliance_status'] = self._determine_compliance_status(
                evaluation
            )

            return evaluation

        except Exception as e:
            self.logger.error(f"Error in evaluate_legal_compliance: {str(e)}")
            raise

    def _initialize_local_storage(self):
        """Initialize SQLite database for compliance data"""
        try:
            os.makedirs('data', exist_ok=True)
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

            # Create tables for compliance data
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS compliance_records (
                    id TEXT PRIMARY KEY,
                    contract_id TEXT,
                    evaluation_data TEXT,
                    timestamp DATETIME
                )
            ''')

            self.conn.commit()

        except Exception as e:
            self.logger.error(f"Error initializing local storage: {str(e)}")
            raise

    def _load_indian_legal_requirements(self):
        """Load Indian legal requirements and regulations"""
        self.legal_requirements = {
            'central_laws': {
                'contract_act': {
                    'name': 'Indian Contract Act, 1872',
                    'sections': {
                        'valid_contract': ['Section 10', 'Section 11'],
                        'consideration': ['Section 23', 'Section 25'],
                        'void_agreements': ['Section 24-30']
                    }
                },
                'specific_relief': {
                    'name': 'Specific Relief Act, 1963',
                    'sections': {
                        'enforcement': ['Section 9', 'Section 10']
                    }
                },
                'it_act': {
                    'name': 'Information Technology Act, 2000',
                    'sections': {
                        'digital_signatures': ['Section 3', 'Section 4']
                    }
                }
            },
            'state_laws': {
                'Maharashtra': {
                    'stamp_act': {
                        'name': 'Maharashtra Stamp Act',
                        'requirements': {}
                    },
                    'rent_control': {
                        'name': 'Maharashtra Rent Control Act',
                        'requirements': {}
                    }
                }
                # Add other states
            },
            'regulatory_requirements': {
                'rbi': {
                    'name': 'RBI Regulations',
                    'applicable_to': ['lending', 'banking', 'foreign_exchange']
                },
                'sebi': {
                    'name': 'SEBI Regulations',
                    'applicable_to': ['securities', 'investments']
                }
            }
        }

    def _check_central_law_compliance(
        self,
        contract: Dict,
        contract_type: str
    ) -> List[ComplianceIssue]:
        """Check compliance with Indian central laws"""
        issues = []
        try:
            # Check Contract Act compliance
            contract_act_issues = self._check_contract_act_compliance(
                contract
            )
            issues.extend(contract_act_issues)

            # Check specific acts based on contract type
            if contract_type == 'employment':
                issues.extend(self._check_labor_law_compliance(contract))
            elif contract_type == 'property':
                issues.extend(self._check_property_law_compliance(contract))
            elif contract_type == 'service':
                issues.extend(self._check_service_contract_compliance(contract))

            return issues

        except Exception as e:
            self.logger.error(f"Error checking central law compliance: {str(e)}")
            return issues

    def _check_state_compliance(
        self,
        contract: Dict,
        jurisdiction: str
    ) -> List[ComplianceIssue]:
        """Check compliance with state-specific laws"""
        issues = []
        try:
            state_laws = self.legal_requirements['state_laws'].get(jurisdiction, {})
            
            for law_name, law_details in state_laws.items():
                law_issues = self._check_specific_law_compliance(
                    contract,
                    law_details
                )
                issues.extend(law_issues)

            return issues

        except Exception as e:
            self.logger.error(f"Error checking state compliance: {str(e)}")
            return issues

    def _check_stamp_duty_requirements(
        self,
        contract: Dict,
        jurisdiction: str,
        contract_type: str
    ) -> Dict:
        """Check stamp duty requirements"""
        try:
            stamp_duty_info = {
                'required': True,
                'amount': self._calculate_stamp_duty(
                    contract,
                    jurisdiction,
                    contract_type
                ),
                'payment_method': self._get_stamp_duty_payment_methods(jurisdiction),
                'compliance_status': 'pending'
            }

            return stamp_duty_info

        except Exception as e:
            self.logger.error(f"Error checking stamp duty requirements: {str(e)}")
            return {'required': True, 'compliance_status': 'error'}

    def _check_registration_requirements(
        self,
        contract: Dict,
        jurisdiction: str
    ) -> Dict:
        """Check registration requirements under Registration Act"""
        try:
            registration_info = {
                'required': self._is_registration_required(contract),
                'authority': self._get_registration_authority(jurisdiction),
                'time_limit': '4 months',
                'compliance_status': 'pending'
            }

            return registration_info

        except Exception as e:
            self.logger.error(f"Error checking registration requirements: {str(e)}")
            return {'required': True, 'compliance_status': 'error'}

    def _generate_recommendations(
        self,
        issues: List[ComplianceIssue],
        stamp_duty: Dict,
        registration: Dict
    ) -> List[Dict]:
        """Generate recommendations for compliance"""
        recommendations = []
        try:
            # Process critical issues first
            critical_issues = [i for i in issues if i.severity == 'critical']
            for issue in critical_issues:
                recommendations.append({
                    'priority': 'high',
                    'issue': issue.description,
                    'recommendation': issue.suggested_remedy,
                    'reference': issue.reference
                })

            # Add stamp duty recommendations
            if stamp_duty.get('required'):
                recommendations.append({
                    'priority': 'high',
                    'issue': 'Stamp Duty Requirement',
                    'recommendation': f"Pay stamp duty of amount {stamp_duty.get('amount')}",
                    'reference': 'State Stamp Act'
                })

            # Add registration recommendations
            if registration.get('required'):
                recommendations.append({
                    'priority': 'high',
                    'issue': 'Registration Requirement',
                    'recommendation': 'Register document within 4 months',
                    'reference': 'Registration Act, 1908'
                })

            return recommendations

        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return recommendations

    def _determine_compliance_status(self, evaluation: Dict) -> str:
        """Determine overall compliance status"""
        try:
            critical_issues = any(
                i.severity == 'critical'
                for i in evaluation['issues']
            )
            
            if critical_issues:
                return 'non_compliant'
            elif evaluation['issues']:
                return 'partially_compliant'
            else:
                return 'compliant'

        except Exception as e:
            self.logger.error(f"Error determining compliance status: {str(e)}")
            return 'unknown'

    def get_compliance_summary(
        self,
        evaluation: Dict,
        detailed: bool = False
    ) -> Dict:
        """Generate human-readable compliance summary"""
        try:
            summary = {
                'overall_status': evaluation['compliance_status'],
                'critical_issues': len([
                    i for i in evaluation['issues']
                    if i.severity == 'critical'
                ]),
                'stamp_duty_status': evaluation['stamp_duty']['compliance_status'],
                'registration_status': evaluation['registration']['compliance_status'],
                'key_recommendations': [
                    r for r in evaluation['recommendations']
                    if r['priority'] == 'high'
                ]
            }

            if detailed:
                summary['full_issues'] = evaluation['issues']
                summary['regulatory_details'] = evaluation['regulatory_checks']

            return summary

        except Exception as e:
            self.logger.error(f"Error generating compliance summary: {str(e)}")
            return {}

    def __del__(self):
        """Cleanup database connection"""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
        except Exception as e:
            self.logger.error(f"Error closing database connection: {str(e)}")