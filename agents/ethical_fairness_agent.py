# agents/ethical_fairness_agent.py
from libraries import *
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid

class BiasLevel(Enum):
    """Bias severity levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class EthicalIssue:
    """Data structure for ethical issues"""
    issue_id: str
    category: str  # 'bias', 'fairness', 'discrimination', 'ethics'
    level: BiasLevel
    description: str
    location: str
    original_text: str
    suggested_revision: str
    justification: str

class EthicalFairnessAgent:
    """
    Ethical & Fairness Agent for ensuring contract fairness and neutrality.
    Detects bias and discriminatory language while promoting ethical standards.
    """
    def __init__(self, llm: OpenAI = None):
        self.logger = logging.getLogger(__name__)
        self.llm = llm or OpenAI(temperature=0.2)
        self._load_ethical_standards()
        self._load_bias_patterns()

    def evaluate_contract_ethics(
        self,
        contract: Dict,
        industry: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Perform comprehensive ethical evaluation of the contract.
        
        Args:
            contract (Dict): Contract to evaluate
            industry (str): Industry context
            context (Dict, optional): Additional context
            
        Returns:
            Dict: Complete ethical evaluation results
        """
        try:
            evaluation = {
                'timestamp': datetime.now().isoformat(),
                'contract_id': contract.get('metadata', {}).get('id'),
                'ethical_score': 0.0,
                'bias_detection': {},
                'fairness_analysis': {},
                'ethical_compliance': {},
                'issues': [],
                'recommendations': []
            }

            # 1. Detect Bias
            evaluation['bias_detection'] = self._detect_bias(contract)

            # 2. Analyze Fairness
            evaluation['fairness_analysis'] = self._analyze_fairness(contract)

            # 3. Check Ethical Compliance
            evaluation['ethical_compliance'] = self._check_ethical_compliance(
                contract,
                industry
            )

            # 4. Compile Issues
            evaluation['issues'] = self._compile_ethical_issues(
                evaluation['bias_detection'],
                evaluation['fairness_analysis'],
                evaluation['ethical_compliance']
            )

            # 5. Generate Recommendations
            evaluation['recommendations'] = self._generate_recommendations(
                evaluation['issues']
            )

            # 6. Calculate Overall Score
            evaluation['ethical_score'] = self._calculate_ethical_score(evaluation)

            return evaluation

        except Exception as e:
            self.logger.error(f"Error in evaluate_contract_ethics: {str(e)}")
            raise

    def _detect_bias(self, contract: Dict) -> Dict:
        """Detect biased language and unfair terms."""
        try:
            bias_results = {
                'language_bias': [],
                'structural_bias': [],
                'party_bias': [],
                'score': 0.0
            }

            # Check for biased language
            bias_results['language_bias'] = self._analyze_language_bias(contract)
            
            # Check for structural bias
            bias_results['structural_bias'] = self._analyze_structural_bias(contract)
            
            # Check for party bias
            bias_results['party_bias'] = self._analyze_party_bias(contract)
            
            # Calculate bias score
            bias_results['score'] = self._calculate_bias_score(bias_results)
            
            return bias_results
            
        except Exception as e:
            self.logger.error(f"Error in bias detection: {str(e)}")
            raise

    def _analyze_fairness(self, contract: Dict) -> Dict:
        """Analyze the fairness of contract terms and obligations."""
        try:
            fairness_results = {
                'obligation_balance': self._analyze_obligations(contract),
                'rights_balance': self._analyze_rights(contract),
                'remedy_balance': self._analyze_remedies(contract),
                'power_balance': self._analyze_power_dynamics(contract),
                'score': 0.0
            }
            
            # Calculate overall fairness score
            fairness_results['score'] = self._calculate_fairness_score(
                fairness_results
            )
            
            return fairness_results
            
        except Exception as e:
            self.logger.error(f"Error in fairness analysis: {str(e)}")
            raise

    def _check_ethical_compliance(
        self,
        contract: Dict,
        industry: str
    ) -> Dict:
        """Check compliance with ethical standards."""
        try:
            compliance_results = {
                'industry_standards': self._check_industry_standards(
                    contract,
                    industry
                ),
                'professional_ethics': self._check_professional_ethics(contract),
                'discrimination_check': self._check_discrimination(contract),
                'score': 0.0
            }
            
            # Calculate compliance score
            compliance_results['score'] = self._calculate_compliance_score(
                compliance_results
            )
            
            return compliance_results
            
        except Exception as e:
            self.logger.error(f"Error in ethical compliance check: {str(e)}")
            raise

    def _generate_recommendations(
        self,
        issues: List[EthicalIssue]
    ) -> List[Dict]:
        """Generate recommendations for addressing ethical issues."""
        try:
            recommendations = []
            
            for issue in issues:
                if issue.level in [BiasLevel.HIGH, BiasLevel.CRITICAL]:
                    recommendations.append({
                        'priority': 'high',
                        'category': issue.category,
                        'issue': issue.description,
                        'location': issue.location,
                        'current_text': issue.original_text,
                        'suggested_revision': issue.suggested_revision,
                        'justification': issue.justification
                    })
                else:
                    recommendations.append({
                        'priority': 'medium',
                        'category': issue.category,
                        'issue': issue.description,
                        'suggestion': issue.suggested_revision,
                        'justification': issue.justification
                    })
            
            return sorted(
                recommendations,
                key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['priority']]
            )
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            raise

    def _analyze_language_bias(self, contract: Dict) -> List[EthicalIssue]:
        """Analyze contract language for bias."""
        bias_issues = []
        
        try:
            for section_name, section_content in contract['sections'].items():
                for clause in section_content:
                    # Check against bias patterns
                    for pattern in self.bias_patterns['language']:
                        if self._matches_bias_pattern(
                            clause['content'],
                            pattern
                        ):
                            bias_issues.append(
                                EthicalIssue(
                                    issue_id=str(uuid.uuid4()),
                                    category='bias',
                                    level=BiasLevel(pattern['level']),
                                    description=pattern['description'],
                                    location=f"{section_name}: {clause['heading']}",
                                    original_text=clause['content'],
                                    suggested_revision=self._generate_neutral_language(
                                        clause['content'],
                                        pattern
                                    ),
                                    justification=pattern['justification']
                                )
                            )
            
            return bias_issues
            
        except Exception as e:
            self.logger.error(f"Error in language bias analysis: {str(e)}")
            raise

    def _analyze_obligations(self, contract: Dict) -> Dict:
        """Analyze the balance of obligations between parties."""
        try:
            parties = self._extract_parties(contract)
            obligations = {party: [] for party in parties}
            
            for section in contract['sections'].values():
                for clause in section:
                    if 'shall' in clause['content'].lower():
                        obligations_found = self._extract_obligations(
                            clause['content']
                        )
                        for party, obligation in obligations_found.items():
                            obligations[party].extend(obligation)
            
            return {
                'distribution': {
                    party: len(obls) for party, obls in obligations.items()
                },
                'balance_score': self._calculate_obligation_balance(obligations)
            }
            
        except Exception as e:
            self.logger.error(f"Error in obligations analysis: {str(e)}")
            raise

    def get_ethical_summary(
        self,
        evaluation: Dict,
        detailed: bool = False
    ) -> Dict:
        """Generate a human-readable ethical evaluation summary."""
        try:
            summary = {
                'ethical_score': evaluation['ethical_score'],
                'critical_issues': [
                    issue for issue in evaluation['issues']
                    if issue.level in [BiasLevel.HIGH, BiasLevel.CRITICAL]
                ],
                'key_recommendations': [
                    rec for rec in evaluation['recommendations']
                    if rec['priority'] == 'high'
                ]
            }
            
            if detailed:
                summary.update({
                    'bias_analysis': evaluation['bias_detection'],
                    'fairness_metrics': evaluation['fairness_analysis'],
                    'compliance_status': evaluation['ethical_compliance']
                })
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating ethical summary: {str(e)}")
            return {}