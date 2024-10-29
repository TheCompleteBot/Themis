# agents/amendment_tracking_agent.py
from libraries import *
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from datetime import datetime,timedelta
import uuid

@dataclass
class LegalUpdate:
    """Data structure for legal updates"""
    update_id: str = str(uuid.uuid4())
    jurisdiction: str
    category: str  # 'law', 'regulation', 'case_law'
    title: str
    description: str
    effective_date: datetime
    source: str
    impact_level: str  # 'high', 'medium', 'low'
    affected_areas: List[str]
    timestamp: datetime = datetime.now()

@dataclass
class Amendment:
    """Data structure for contract amendments"""
    amendment_id: str = str(uuid.uuid4())
    contract_id: str
    legal_update_id: str
    affected_clauses: List[str]
    original_text: str
    proposed_text: str
    status: str  # 'proposed', 'approved', 'implemented'
    justification: str
    timestamp: datetime = datetime.now()

class AmendmentTrackingAgent:
    """
    Amendment Tracking Agent for monitoring legal changes and managing contract amendments.
    Tracks legal updates and suggests necessary contract modifications.
    """
    def __init__(self, llm: OpenAI = None):
        self.logger = logging.getLogger(__name__)
        self.llm = llm or OpenAI(temperature=0.2)
        self.legal_updates = []
        self.amendments = []
        self._initialize_tracking_system()

    def track_legal_changes(
        self,
        jurisdiction: str,
        categories: Optional[List[str]] = None,
        start_date: Optional[datetime] = None
    ) -> List[LegalUpdate]:
        """
        Track legal changes in specified jurisdiction.
        
        Args:
            jurisdiction (str): Legal jurisdiction to monitor
            categories (List[str], optional): Types of legal changes to track
            start_date (datetime, optional): Start date for tracking
            
        Returns:
            List[LegalUpdate]: Relevant legal updates
        """
        try:
            if not categories:
                categories = ['law', 'regulation', 'case_law']
                
            updates = []
            
            for category in categories:
                # Fetch updates for each category
                category_updates = self._fetch_legal_updates(
                    jurisdiction,
                    category,
                    start_date
                )
                
                # Filter relevant updates
                relevant_updates = self._filter_relevant_updates(
                    category_updates
                )
                
                updates.extend(relevant_updates)
            
            # Store new updates
            self.legal_updates.extend(updates)
            
            return updates
            
        except Exception as e:
            self.logger.error(f"Error tracking legal changes: {str(e)}")
            raise

    def analyze_impact(
        self,
        contract: Dict,
        legal_updates: List[LegalUpdate]
    ) -> Dict:
        """
        Analyze how legal changes affect a contract.
        
        Args:
            contract (Dict): Contract to analyze
            legal_updates (List[LegalUpdate]): Legal changes to consider
            
        Returns:
            Dict: Impact analysis results
        """
        try:
            impact_analysis = {
                'contract_id': contract.get('id'),
                'timestamp': datetime.now().isoformat(),
                'affected_clauses': [],
                'risk_assessment': {},
                'required_actions': []
            }
            
            for update in legal_updates:
                # Analyze impact on specific clauses
                affected_clauses = self._identify_affected_clauses(
                    contract,
                    update
                )
                
                if affected_clauses:
                    impact_analysis['affected_clauses'].extend(affected_clauses)
                    
                    # Assess risks
                    risks = self._assess_update_risks(
                        contract,
                        update,
                        affected_clauses
                    )
                    impact_analysis['risk_assessment'].update(risks)
                    
                    # Determine required actions
                    actions = self._determine_required_actions(
                        update,
                        affected_clauses,
                        risks
                    )
                    impact_analysis['required_actions'].extend(actions)
            
            return impact_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing impact: {str(e)}")
            raise

    def generate_amendments(
        self,
        contract: Dict,
        impact_analysis: Dict
    ) -> List[Amendment]:
        """
        Generate proposed amendments based on impact analysis.
        
        Args:
            contract (Dict): Contract to amend
            impact_analysis (Dict): Impact analysis results
            
        Returns:
            List[Amendment]: Proposed amendments
        """
        try:
            amendments = []
            
            for action in impact_analysis['required_actions']:
                # Generate specific amendments
                if action['type'] == 'modify':
                    amendment = self._generate_modification_amendment(
                        contract,
                        action
                    )
                elif action['type'] == 'add':
                    amendment = self._generate_addition_amendment(
                        contract,
                        action
                    )
                elif action['type'] == 'remove':
                    amendment = self._generate_removal_amendment(
                        contract,
                        action
                    )
                
                amendments.append(amendment)
            
            # Store amendments
            self.amendments.extend(amendments)
            
            return amendments
            
        except Exception as e:
            self.logger.error(f"Error generating amendments: {str(e)}")
            raise

    def notify_updates(
        self,
        contract_id: str,
        stakeholders: List[str]
    ) -> Dict:
        """
        Notify stakeholders of legal updates and required amendments.
        
        Args:
            contract_id (str): Contract identifier
            stakeholders (List[str]): List of stakeholders to notify
            
        Returns:
            Dict: Notification results
        """
        try:
            # Get relevant updates and amendments
            relevant_updates = self._get_pending_updates(contract_id)
            pending_amendments = self._get_pending_amendments(contract_id)
            
            notification = self._prepare_notification(
                relevant_updates,
                pending_amendments
            )
            
            # Send notifications
            results = {
                'timestamp': datetime.now().isoformat(),
                'contract_id': contract_id,
                'notifications_sent': []
            }
            
            for stakeholder in stakeholders:
                result = self._send_notification(
                    stakeholder,
                    notification
                )
                results['notifications_sent'].append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error sending notifications: {str(e)}")
            raise

    def _identify_affected_clauses(
        self,
        contract: Dict,
        update: LegalUpdate
    ) -> List[Dict]:
        """Identify clauses affected by legal update."""
        affected_clauses = []
        
        try:
            for section_name, section_content in contract['sections'].items():
                for clause in section_content:
                    if self._is_clause_affected(clause, update):
                        affected_clauses.append({
                            'section': section_name,
                            'clause': clause,
                            'impact_details': self._analyze_clause_impact(
                                clause,
                                update
                            )
                        })
            
            return affected_clauses
            
        except Exception as e:
            self.logger.error(f"Error identifying affected clauses: {str(e)}")
            return affected_clauses

    def _generate_modification_amendment(
        self,
        contract: Dict,
        action: Dict
    ) -> Amendment:
        """Generate amendment for clause modification."""
        try:
            # Extract original text
            original_text = self._extract_clause_text(
                contract,
                action['clause']
            )
            
            # Generate proposed text
            proposed_text = self._generate_updated_clause(
                original_text,
                action['requirements']
            )
            
            return Amendment(
                contract_id=contract.get('id', ''),
                legal_update_id=action['update_id'],
                affected_clauses=[action['clause']],
                original_text=original_text,
                proposed_text=proposed_text,
                status='proposed',
                justification=action['justification']
            )
            
        except Exception as e:
            self.logger.error(f"Error generating modification amendment: {str(e)}")
            raise

    def get_amendment_status(
        self,
        contract_id: str
    ) -> Dict:
        """Get status of all amendments for a contract."""
        try:
            contract_amendments = [
                a for a in self.amendments
                if a.contract_id == contract_id
            ]
            
            return {
                'contract_id': contract_id,
                'total_amendments': len(contract_amendments),
                'by_status': {
                    'proposed': len([a for a in contract_amendments if a.status == 'proposed']),
                    'approved': len([a for a in contract_amendments if a.status == 'approved']),
                    'implemented': len([a for a in contract_amendments if a.status == 'implemented'])
                },
                'latest_update': max(
                    (a.timestamp for a in contract_amendments),
                    default=None
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error getting amendment status: {str(e)}")
            return {}

    def _initialize_tracking_system(self):
        """Initialize the legal tracking system."""
        self.tracking_config = {
            'update_frequency': timedelta(days=1),
            'jurisdictions': set(),
            'categories': {
                'law': True,
                'regulation': True,
                'case_law': True
            },
            'notification_preferences': {},
            'last_check': datetime.now()
        }