# agents/contract_comparison_agent.py
from libraries import *
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class ComparisonResult:
    """Data structure for contract comparison results"""
    comparison_id: str = str(uuid.uuid4())
    source_contract_id: str
    target_contract_id: str
    similarities: Dict
    differences: Dict
    recommendations: List[Dict]
    timestamp: datetime = datetime.now()

class ContractComparisonAgent:
    """
    Contract Comparison Agent for analyzing differences between contracts
    and suggesting improvements based on best practices.
    """
    def __init__(self, llm: OpenAI = None):
        self.logger = logging.getLogger(__name__)
        self.llm = llm or OpenAI(temperature=0.2)
        self._load_best_practices()
        self.comparison_history = []

    def compare_contracts(
        self,
        source_contract: Dict,
        target_contract: Dict,
        comparison_type: str = 'detailed'
    ) -> ComparisonResult:
        """
        Compare two contracts and generate analysis.
        
        Args:
            source_contract (Dict): Primary contract for comparison
            target_contract (Dict): Contract to compare against
            comparison_type (str): Level of comparison detail
            
        Returns:
            ComparisonResult: Detailed comparison analysis
        """
        try:
            # Perform structural comparison
            structural_diff = self._compare_structure(
                source_contract,
                target_contract
            )
            
            # Compare content
            content_diff = self._compare_content(
                source_contract,
                target_contract
            )
            
            # Analyze clauses
            clause_analysis = self._analyze_clauses(
                source_contract,
                target_contract
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                structural_diff,
                content_diff,
                clause_analysis
            )
            
            result = ComparisonResult(
                source_contract_id=source_contract.get('id', ''),
                target_contract_id=target_contract.get('id', ''),
                similarities=self._find_similarities(
                    structural_diff,
                    content_diff
                ),
                differences={
                    'structural': structural_diff,
                    'content': content_diff,
                    'clauses': clause_analysis
                },
                recommendations=recommendations
            )
            
            # Store comparison history
            self.comparison_history.append(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in contract comparison: {str(e)}")
            raise

    def analyze_best_practices(
        self,
        contract: Dict,
        industry: str,
        jurisdiction: str
    ) -> Dict:
        """
        Compare contract against industry best practices.
        
        Args:
            contract (Dict): Contract to analyze
            industry (str): Industry context
            jurisdiction (str): Legal jurisdiction
            
        Returns:
            Dict: Best practice analysis and recommendations
        """
        try:
            best_practices = self._get_industry_best_practices(
                industry,
                jurisdiction
            )
            
            analysis = {
                'compliance_score': 0,
                'matches': [],
                'gaps': [],
                'recommendations': []
            }
            
            # Check each best practice
            for practice in best_practices:
                result = self._check_best_practice_compliance(
                    contract,
                    practice
                )
                
                if result['compliant']:
                    analysis['matches'].append(result)
                else:
                    analysis['gaps'].append(result)
                    analysis['recommendations'].append(
                        self._generate_practice_recommendation(result)
                    )
            
            # Calculate compliance score
            analysis['compliance_score'] = len(analysis['matches']) / len(best_practices)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in best practice analysis: {str(e)}")
            raise

    def track_changes(
        self,
        original_contract: Dict,
        modified_contract: Dict
    ) -> Dict:
        """
        Track and visualize changes between contract versions.
        
        Args:
            original_contract (Dict): Original contract version
            modified_contract (Dict): Modified contract version
            
        Returns:
            Dict: Detailed change analysis
        """
        try:
            changes = {
                'timestamp': datetime.now().isoformat(),
                'additions': [],
                'deletions': [],
                'modifications': [],
                'summary': {}
            }
            
            # Track section changes
            for section_name in set(original_contract['sections'].keys()) | \
                              set(modified_contract['sections'].keys()):
                
                section_changes = self._track_section_changes(
                    original_contract.get('sections', {}).get(section_name, []),
                    modified_contract.get('sections', {}).get(section_name, [])
                )
                
                changes['additions'].extend(section_changes['additions'])
                changes['deletions'].extend(section_changes['deletions'])
                changes['modifications'].extend(section_changes['modifications'])
            
            # Generate change summary
            changes['summary'] = self._generate_change_summary(changes)
            
            return changes
            
        except Exception as e:
            self.logger.error(f"Error tracking changes: {str(e)}")
            raise

    def _compare_structure(
        self,
        source_contract: Dict,
        target_contract: Dict
    ) -> Dict:
        """Compare contract structures and organization."""
        try:
            structural_diff = {
                'missing_sections': [],
                'additional_sections': [],
                'section_order': [],
                'formatting_differences': []
            }
            
            # Compare sections
            source_sections = set(source_contract['sections'].keys())
            target_sections = set(target_contract['sections'].keys())
            
            structural_diff['missing_sections'] = list(
                target_sections - source_sections
            )
            structural_diff['additional_sections'] = list(
                source_sections - target_sections
            )
            
            # Compare section order
            structural_diff['section_order'] = self._compare_section_order(
                source_contract,
                target_contract
            )
            
            # Compare formatting
            structural_diff['formatting_differences'] = \
                self._compare_formatting(
                    source_contract,
                    target_contract
                )
            
            return structural_diff
            
        except Exception as e:
            self.logger.error(f"Error comparing structure: {str(e)}")
            raise

    def _compare_content(
        self,
        source_contract: Dict,
        target_contract: Dict
    ) -> Dict:
        """Compare contract content and language."""
        try:
            content_diff = {
                'text_differences': [],
                'semantic_differences': [],
                'terminology_differences': []
            }
            
            # Compare each section's content
            common_sections = set(source_contract['sections'].keys()) & \
                            set(target_contract['sections'].keys())
            
            for section in common_sections:
                # Text comparison
                text_diff = self._compare_text(
                    source_contract['sections'][section],
                    target_contract['sections'][section]
                )
                content_diff['text_differences'].extend(text_diff)
                
                # Semantic comparison
                semantic_diff = self._compare_semantics(
                    source_contract['sections'][section],
                    target_contract['sections'][section]
                )
                content_diff['semantic_differences'].extend(semantic_diff)
                
                # Terminology comparison
                term_diff = self._compare_terminology(
                    source_contract['sections'][section],
                    target_contract['sections'][section]
                )
                content_diff['terminology_differences'].extend(term_diff)
            
            return content_diff
            
        except Exception as e:
            self.logger.error(f"Error comparing content: {str(e)}")
            raise

    def _generate_recommendations(
        self,
        structural_diff: Dict,
        content_diff: Dict,
        clause_analysis: Dict
    ) -> List[Dict]:
        """Generate improvement recommendations based on comparison."""
        try:
            recommendations = []
            
            # Structure recommendations
            if structural_diff['missing_sections']:
                recommendations.extend(
                    self._generate_structure_recommendations(structural_diff)
                )
            
            # Content recommendations
            if content_diff['semantic_differences']:
                recommendations.extend(
                    self._generate_content_recommendations(content_diff)
                )
            
            # Clause recommendations
            recommendations.extend(
                self._generate_clause_recommendations(clause_analysis)
            )
            
            return self._prioritize_recommendations(recommendations)
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def get_comparison_summary(
        self,
        comparison_result: ComparisonResult
    ) -> Dict:
        """Generate a human-readable comparison summary."""
        try:
            return {
                'comparison_id': comparison_result.comparison_id,
                'timestamp': comparison_result.timestamp.isoformat(),
                'key_differences': self._summarize_differences(
                    comparison_result.differences
                ),
                'key_recommendations': [
                    rec for rec in comparison_result.recommendations
                    if rec.get('priority') == 'high'
                ],
                'similarity_score': self._calculate_similarity_score(
                    comparison_result.similarities
                )
            }
        except Exception as e:
            self.logger.error(f"Error generating comparison summary: {str(e)}")
            return {}

    def _load_best_practices(self):
        """Load industry best practices and standards."""
        # This would typically load from a database or file
        self.best_practices = {
            'general': [
                {
                    'category': 'structure',
                    'description': 'Clear section organization',
                    'requirements': []
                }
                # Add more best practices
            ],
            'industry_specific': {
                'technology': [],
                'healthcare': [],
                'finance': []
            }
        }