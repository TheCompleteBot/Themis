# agents/risk_assessment_agent.py
from libraries import *
from typing import List, Dict, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid

class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Risk:
    """Data structure for identified risks"""
    risk_id: str
    category: str  # 'legal', 'financial', 'operational'
    level: RiskLevel
    description: str
    impact: str
    probability: float
    clause_reference: str
    mitigation_suggestion: str

class RiskAssessmentAgent:
    """
    Risk Assessment Agent for evaluating contract risks and liabilities.
    Identifies potential issues and suggests mitigation strategies.
    """
    def __init__(self, llm: OpenAI = None):
        self.logger = logging.getLogger(__name__)
        self.llm = llm or OpenAI(temperature=0.2)
        self._load_risk_patterns()
        
    def assess_contract_risks(
        self,
        contract: Dict,
        context: Dict
    ) -> Dict:
        """
        Perform comprehensive risk assessment of the contract.
        
        Args:
            contract (Dict): Contract to assess
            context (Dict): Additional context (industry, jurisdiction, etc.)
            
        Returns:
            Dict: Complete risk assessment results
        """
        try:
            assessment = {
                'timestamp': datetime.now().isoformat(),
                'contract_id': contract.get('metadata', {}).get('id'),
                'overall_risk_level': None,
                'risks_by_category': {},
                'liability_analysis': {},
                'ambiguities': [],
                'risk_score': 0.0,
                'recommendations': []
            }

            # 1. Identify risks
            risks = self._identify_risks(contract, context)
            assessment['risks_by_category'] = self._categorize_risks(risks)

            # 2. Analyze liability allocation
            assessment['liability_analysis'] = self._analyze_liabilities(contract)

            # 3. Detect ambiguities
            assessment['ambiguities'] = self._detect_ambiguities(contract)

            # 4. Calculate risk scores
            assessment['risk_score'] = self._calculate_risk_score(risks)
            assessment['overall_risk_level'] = self._determine_risk_level(
                assessment['risk_score']
            )

            # 5. Generate recommendations
            assessment['recommendations'] = self._generate_recommendations(
                risks,
                assessment['liability_analysis'],
                assessment['ambiguities']
            )

            return assessment

        except Exception as e:
            self.logger.error(f"Error in assess_contract_risks: {str(e)}")
            raise

    def _identify_risks(
        self,
        contract: Dict,
        context: Dict
    ) -> List[Risk]:
        """Identify various types of risks in the contract."""
        risks = []
        
        # Analyze each section for risks
        for section_name, section_content in contract['sections'].items():
            # Legal risks
            legal_risks = self._identify_legal_risks(
                section_content,
                context
            )
            risks.extend(legal_risks)
            
            # Financial risks
            financial_risks = self._identify_financial_risks(
                section_content,
                context
            )
            risks.extend(financial_risks)
            
            # Operational risks
            operational_risks = self._identify_operational_risks(
                section_content,
                context
            )
            risks.extend(operational_risks)

        return risks

    def _analyze_liabilities(self, contract: Dict) -> Dict:
        """Analyze liability allocation between parties."""
        try:
            analysis = {
                'liability_distribution': {},
                'imbalances': [],
                'high_risk_obligations': []
            }
            
            # Extract parties
            parties = self._extract_parties(contract)
            
            # Initialize liability tracking for each party
            for party in parties:
                analysis['liability_distribution'][party] = {
                    'obligations': [],
                    'risks': [],
                    'protections': []
                }
            
            # Analyze each clause for liability implications
            for section in contract['sections'].values():
                for clause in section:
                    liability_info = self._analyze_clause_liability(
                        clause,
                        parties
                    )
                    
                    # Update liability distribution
                    for party, liabilities in liability_info.items():
                        analysis['liability_distribution'][party]['obligations'].extend(
                            liabilities.get('obligations', [])
                        )
                        analysis['liability_distribution'][party]['risks'].extend(
                            liabilities.get('risks', [])
                        )
                        analysis['liability_distribution'][party]['protections'].extend(
                            liabilities.get('protections', [])
                        )
            
            # Identify imbalances
            analysis['imbalances'] = self._identify_liability_imbalances(
                analysis['liability_distribution']
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in liability analysis: {str(e)}")
            raise

    def _detect_ambiguities(self, contract: Dict) -> List[Dict]:
        """Detect ambiguous language and potential areas of dispute."""
        ambiguities = []
        
        try:
            for section_name, section_content in contract['sections'].items():
                section_ambiguities = self._analyze_section_ambiguity(
                    section_content,
                    section_name
                )
                ambiguities.extend(section_ambiguities)
            
            return ambiguities
            
        except Exception as e:
            self.logger.error(f"Error in ambiguity detection: {str(e)}")
            raise

    def _calculate_risk_score(self, risks: List[Risk]) -> float:
        """Calculate overall risk score based on identified risks."""
        try:
            if not risks:
                return 0.0
                
            # Risk level weights
            weights = {
                RiskLevel.LOW: 1,
                RiskLevel.MEDIUM: 2,
                RiskLevel.HIGH: 3,
                RiskLevel.CRITICAL: 4
            }
            
            # Calculate weighted score
            total_weight = sum(weights[risk.level] * risk.probability for risk in risks)
            max_possible_weight = len(risks) * weights[RiskLevel.CRITICAL]
            
            return (total_weight / max_possible_weight) * 100 if max_possible_weight else 0
            
        except Exception as e:
            self.logger.error(f"Error in risk score calculation: {str(e)}")
            return 0.0

    def _generate_recommendations(
        self,
        risks: List[Risk],
        liability_analysis: Dict,
        ambiguities: List[Dict]
    ) -> List[Dict]:
        """Generate recommendations for risk mitigation."""
        recommendations = []
        
        try:
            # Process high and critical risks first
            priority_risks = [
                risk for risk in risks 
                if risk.level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
            ]
            
            for risk in priority_risks:
                recommendations.append({
                    'priority': 'high',
                    'category': risk.category,
                    'issue': risk.description,
                    'recommendation': risk.mitigation_suggestion,
                    'impact': risk.impact
                })
            
            # Address liability imbalances
            for imbalance in liability_analysis.get('imbalances', []):
                recommendations.append({
                    'priority': 'medium',
                    'category': 'liability',
                    'issue': imbalance['description'],
                    'recommendation': imbalance['suggestion'],
                    'impact': 'Potential legal disputes and unfair risk allocation'
                })
            
            # Address ambiguities
            for ambiguity in ambiguities:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'clarity',
                    'issue': ambiguity['description'],
                    'recommendation': ambiguity['suggestion'],
                    'impact': 'Potential misinterpretation and disputes'
                })
            
            return sorted(
                recommendations,
                key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['priority']]
            )
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def _identify_legal_risks(
        self,
        section_content: List[Dict],
        context: Dict
    ) -> List[Risk]:
        """Identify legal risks in contract sections."""
        legal_risks = []
        
        for clause in section_content:
            # Check against legal risk patterns
            for pattern in self.risk_patterns['legal']:
                if self._matches_risk_pattern(clause['content'], pattern):
                    legal_risks.append(
                        Risk(
                            risk_id=str(uuid.uuid4()),
                            category='legal',
                            level=RiskLevel(pattern['risk_level']),
                            description=pattern['description'],
                            impact=pattern['impact'],
                            probability=self._calculate_risk_probability(
                                clause['content'],
                                pattern
                            ),
                            clause_reference=clause.get('heading', ''),
                            mitigation_suggestion=pattern['mitigation']
                        )
                    )
        
        return legal_risks

    def get_risk_summary(
        self,
        assessment: Dict,
        detailed: bool = False
    ) -> Dict:
        """Generate a human-readable risk assessment summary."""
        try:
            summary = {
                'overall_risk_level': assessment['overall_risk_level'],
                'risk_score': assessment['risk_score'],
                'high_priority_risks': [
                    risk for risk in assessment['risks_by_category'].get('all', [])
                    if risk.level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
                ],
                'key_recommendations': [
                    rec for rec in assessment['recommendations']
                    if rec['priority'] == 'high'
                ]
            }
            
            if detailed:
                summary.update({
                    'liability_imbalances': assessment['liability_analysis']['imbalances'],
                    'ambiguities': assessment['ambiguities'],
                    'risk_distribution': self._calculate_risk_distribution(
                        assessment['risks_by_category']
                    )
                })
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating risk summary: {str(e)}")
            return {}

    def _load_risk_patterns(self):
        """Load risk patterns and indicators."""
        self.risk_patterns = {
            'legal': [
                {
                    'pattern': r'worldwide.*restrict',
                    'risk_level': 'high',
                    'description': 'Overly broad geographical restrictions',
                    'impact': 'May be unenforceable in many jurisdictions',
                    'mitigation': 'Limit geographical scope to specific regions'
                },
                # Add more patterns as needed
            ],
            'financial': [
                {
                    'pattern': r'unlimited.*liability',
                    'risk_level': 'critical',
                    'description': 'Unlimited liability clause',
                    'impact': 'Excessive financial exposure',
                    'mitigation': 'Add reasonable liability caps'
                },
                # Add more patterns
            ],
            'operational': [
                {
                    'pattern': r'immediate.*termination',
                    'risk_level': 'medium',
                    'description': 'Immediate termination clause',
                    'impact': 'Operational disruption risk',
                    'mitigation': 'Add reasonable notice period'
                },
                # Add more patterns
            ]
        }