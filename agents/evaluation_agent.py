# agents/evaluation_agent.py
import logging
from typing import Dict, List
import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')
except Exception as e:
    print(f"Error downloading NLTK data: {e}")

class EvaluationAgent:
    """
    Agent for evaluating contract content and structure.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.lemmatizer = WordNetLemmatizer()
        self._load_evaluation_criteria()

    def _load_evaluation_criteria(self):
        """Load criteria for contract evaluation"""
        self.required_sections = {
            'employment': [
                'position',
                'duties',
                'compensation',
                'term',
                'termination',
                'confidentiality'
            ],
            'lease': [
                'property',
                'term',
                'rent',
                'maintenance',
                'termination'
            ]
        }
        
        self.common_issues = [
            'unclear language',
            'missing dates',
            'undefined terms',
            'ambiguous clauses'
        ]

    def evaluate_contract(self, draft: str) -> Dict:
        """
        Evaluate contract draft for completeness and clarity.
        
        Args:
            draft: Contract text
            
        Returns:
            Dict containing evaluation results
        """
        try:
            evaluation = {
                'completeness': self._check_completeness(draft),
                'clarity': self._check_clarity(draft),
                'structure': self._check_structure(draft),
                'issues': [],
                'suggestions': []
            }
            
            # Compile issues and suggestions
            evaluation['issues'] = self._compile_issues(evaluation)
            evaluation['suggestions'] = self._generate_suggestions(evaluation)
            
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Error evaluating contract: {str(e)}")
            return {'error': str(e)}

    def _check_completeness(self, draft: str) -> Dict:
        """Check if all required sections are present"""
        sections = self._extract_sections(draft)
        missing_sections = []
        
        # Check for common required sections
        common_required = ['parties', 'term', 'signatures']
        for required in common_required:
            if not any(required.lower() in section.lower() for section in sections):
                missing_sections.append(required)
        
        return {
            'has_all_sections': len(missing_sections) == 0,
            'missing_sections': missing_sections
        }

    def _check_clarity(self, draft: str) -> Dict:
        """Check language clarity and readability"""
        sentences = sent_tokenize(draft)
        clarity_issues = []
        
        for sentence in sentences:
            # Check sentence length
            if len(word_tokenize(sentence)) > 30:
                clarity_issues.append(f"Long sentence: {sentence[:50]}...")
                
            # Check for ambiguous terms
            if any(term in sentence.lower() for term in ['reasonable', 'appropriate', 'etc', 'and/or']):
                clarity_issues.append(f"Ambiguous terms in: {sentence[:50]}...")
                
        return {
            'is_clear': len(clarity_issues) == 0,
            'clarity_issues': clarity_issues
        }

    def _check_structure(self, draft: str) -> Dict:
        """Check contract structure"""
        sections = self._extract_sections(draft)
        structure_issues = []
        
        # Check section numbering
        if not self._has_consistent_numbering(sections):
            structure_issues.append("Inconsistent section numbering")
            
        # Check section order
        if not self._has_logical_order(sections):
            structure_issues.append("Sections not in logical order")
            
        return {
            'is_well_structured': len(structure_issues) == 0,
            'structure_issues': structure_issues
        }

    def _extract_sections(self, draft: str) -> List[str]:
        """Extract sections from contract text"""
        sections = []
        current_section = []
        
        for line in draft.split('\n'):
            if re.match(r'^\d+\.|\([a-z]\)|[A-Z]+\.', line.strip()):
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
            elif line.strip():
                current_section.append(line)
                
        if current_section:
            sections.append('\n'.join(current_section))
            
        return sections

    def suggest_improvements(self, draft: str, evaluation: Dict) -> str:
        """Suggest improvements for the contract"""
        improved_draft = draft
        
        # Fix clarity issues
        if 'clarity_issues' in evaluation:
            for issue in evaluation['clarity_issues']:
                improved_draft = self._fix_clarity_issue(improved_draft, issue)
                
        # Fix structure issues
        if 'structure_issues' in evaluation:
            improved_draft = self._fix_structure_issues(improved_draft, evaluation['structure_issues'])
            
        return improved_draft

    def _fix_clarity_issue(self, draft: str, issue: str) -> str:
        """Fix specific clarity issues"""
        if "Long sentence" in issue:
            # Split long sentences
            return self._split_long_sentences(draft)
        elif "Ambiguous terms" in issue:
            # Replace ambiguous terms
            return self._replace_ambiguous_terms(draft)
        return draft

    def _split_long_sentences(self, text: str) -> str:
        """Split long sentences into shorter ones"""
        sentences = sent_tokenize(text)
        result = []
        
        for sentence in sentences:
            if len(word_tokenize(sentence)) > 30:
                # Split at conjunctions or semicolons
                parts = re.split(r';|, and|, but', sentence)
                result.extend(parts)
            else:
                result.append(sentence)
                
        return ' '.join(result)

    def _replace_ambiguous_terms(self, text: str) -> str:
        """Replace ambiguous terms with specific ones"""
        replacements = {
            'reasonable': 'within 5 business days',
            'appropriate': 'as specified in section',
            'etc': '',
            'and/or': 'and'
        }
        
        for ambiguous, specific in replacements.items():
            text = text.replace(ambiguous, specific)
            
        return text

    def _compile_issues(self, evaluation: Dict) -> List[str]:
        """Compile all identified issues"""
        issues = []
        
        if not evaluation['completeness']['has_all_sections']:
            issues.extend([f"Missing section: {section}" 
                         for section in evaluation['completeness']['missing_sections']])
            
        if not evaluation['clarity']['is_clear']:
            issues.extend(evaluation['clarity']['clarity_issues'])
            
        if not evaluation['structure']['is_well_structured']:
            issues.extend(evaluation['structure']['structure_issues'])
            
        return issues

    def _generate_suggestions(self, evaluation: Dict) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        for issue in evaluation['issues']:
            if "Missing section" in issue:
                suggestions.append(f"Add section for {issue.split(':')[1]}")
            elif "Long sentence" in issue:
                suggestions.append("Split long sentences into shorter, clearer ones")
            elif "Ambiguous terms" in issue:
                suggestions.append("Replace ambiguous terms with specific, measurable criteria")
                
        return suggestions