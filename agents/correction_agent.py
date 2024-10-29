from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import uuid

@dataclass
class Correction:
    """Data structure for storing corrections"""
    correction_id: str
    section: str
    original_text: str
    corrected_text: str
    reason: str
    timestamp: datetime

class CorrectionAgent:
    """
    Simplified Correction Agent for implementing feedback and maintaining contract quality.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.corrections_history = []

    def correct_draft(self, contract: Dict) -> Dict:
        """
        Main method to correct a contract draft.
        
        Args:
            contract (Dict): Contract draft to be corrected
            
        Returns:
            Dict: Corrected contract draft
        """
        try:
            # Make a copy of the contract to avoid modifying the original
            corrected_contract = contract.copy()
            
            # Apply standard corrections
            corrected_contract = self._apply_standard_corrections(corrected_contract)
            
            # Log the corrections
            self.logger.info("Contract corrections applied successfully")
            
            return corrected_contract
            
        except Exception as e:
            self.logger.error(f"Error correcting draft: {str(e)}")
            return contract

    def process_feedback(
        self,
        contract: Dict,
        feedback: List[Dict]
    ) -> Tuple[Dict, List[Correction]]:
        """
        Process feedback and implement corrections.
        
        Args:
            contract (Dict): Current contract draft
            feedback (List[Dict]): List of feedback items with format:
                                 {'section': str, 'suggested_change': str, 'reason': str}
            
        Returns:
            Tuple[Dict, List[Correction]]: Updated contract and list of corrections made
        """
        try:
            corrections = []
            updated_contract = contract.copy()
            
            for item in feedback:
                if self._validate_feedback(item):
                    correction = self._implement_correction(updated_contract, item)
                    if correction:
                        corrections.append(correction)
                        updated_contract = self._apply_single_correction(
                            updated_contract,
                            correction
                        )
            
            # Store corrections in history
            self.corrections_history.extend(corrections)
            
            return updated_contract, corrections
            
        except Exception as e:
            self.logger.error(f"Error processing feedback: {str(e)}")
            return contract, []

    def _validate_feedback(self, feedback: Dict) -> bool:
        """Validate feedback format"""
        required_fields = ['section', 'suggested_change', 'reason']
        return all(field in feedback and feedback[field] for field in required_fields)

    def _implement_correction(self, contract: Dict, feedback: Dict) -> Optional[Correction]:
        """Create a correction based on feedback"""
        try:
            section = feedback['section']
            original_text = contract.get(section, '')
            
            if not original_text:
                return None
                
            return Correction(
                correction_id=str(uuid.uuid4()),
                section=section,
                original_text=original_text,
                corrected_text=feedback['suggested_change'],
                reason=feedback['reason'],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error implementing correction: {str(e)}")
            return None

    def _apply_single_correction(self, contract: Dict, correction: Correction) -> Dict:
        """Apply a single correction to the contract"""
        updated_contract = contract.copy()
        try:
            if correction.section in updated_contract:
                updated_contract[correction.section] = correction.corrected_text
            return updated_contract
        except Exception as e:
            self.logger.error(f"Error applying correction: {str(e)}")
            return contract

    def _apply_standard_corrections(self, contract: Dict) -> Dict:
        """Apply standard corrections to the contract"""
        try:
            updated_contract = contract.copy()
            
            # Apply basic formatting corrections
            for section, content in updated_contract.items():
                if isinstance(content, str):
                    # Remove extra whitespace
                    content = ' '.join(content.split())
                    # Ensure proper sentence capitalization
                    content = '. '.join(s.capitalize() for s in content.split('. '))
                    updated_contract[section] = content
            
            return updated_contract
            
        except Exception as e:
            self.logger.error(f"Error applying standard corrections: {str(e)}")
            return contract

    def get_correction_history(self) -> List[Correction]:
        """Get the history of all corrections made"""
        return self.corrections_history