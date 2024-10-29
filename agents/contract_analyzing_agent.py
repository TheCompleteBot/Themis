import logging
from typing import Dict, List, Optional
from openai import OpenAI
import json
import datetime
class ContractAnalyzer:
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.logger = logging.getLogger(__name__)

    def analyze_contract(self, content: str) -> Dict:
        """Analyze contract content with enhanced error handling"""
        try:
            # Clean the content
            cleaned_content = content.strip()
            
            # Default analysis structure
            analysis = {
                "contract_type": "general",
                "key_sections": [],
                "formatting_requirements": {
                    "section_formatting": {"fontSize": 12, "bold": True},
                    "content_formatting": {"fontSize": 10}
                }
            }
            
            # Determine contract type
            if "EMPLOYMENT CONTRACT" in cleaned_content.upper():
                analysis["contract_type"] = "employment"
                analysis["key_sections"] = [
                    "BASIC INFORMATION",
                    "EMPLOYMENT DETAILS",
                    "STATUTORY COMPLIANCE",
                    "ADDITIONAL INFORMATION",
                    "TERMINATION",
                    "LEGAL REFERENCES"
                ]
            elif "SERVICE AGREEMENT" in cleaned_content.upper():
                analysis["contract_type"] = "service"
                analysis["key_sections"] = [
                    "SERVICE DETAILS",
                    "PAYMENT TERMS",
                    "OBLIGATIONS",
                    "TERMINATION"
                ]
            
            # Try AI analysis for additional insights
            try:
                ai_analysis = self._get_ai_analysis(cleaned_content)
                if ai_analysis and isinstance(ai_analysis, dict):
                    # Merge AI insights with default analysis
                    analysis["formatting_requirements"].update(
                        ai_analysis.get("formatting_requirements", {})
                    )
            except Exception as ai_error:
                self.logger.warning(f"AI analysis failed: {str(ai_error)}")

            return analysis

        except Exception as e:
            self.logger.error(f"Error in contract analysis: {str(e)}")
            return {
                "contract_type": "general",
                "key_sections": ["GENERAL TERMS"],
                "formatting_requirements": {
                    "section_formatting": {"fontSize": 12, "bold": True},
                    "content_formatting": {"fontSize": 10}
                }
            }

    def _get_ai_analysis(self, content: str) -> Optional[Dict]:
        """Get AI analysis of contract content"""
        try:
            prompt = f"""Analyze this contract content and provide:
            1. Formatting requirements
            2. Section hierarchy
            3. Special formatting needs
            
            Return as JSON with this structure:
            {{
                "formatting_requirements": {{
                    "section_formatting": {{"fontSize": 12, "bold": true}},
                    "content_formatting": {{"fontSize": 10}},
                    "special_formatting": []
                }}
            }}

            Content: {content[:1000]}  # First 1000 chars for API limit
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a contract analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"Error in AI analysis: {str(e)}")
            return None

    def generate_template(self, analysis: Dict) -> Dict:
        """Generate template based on contract analysis"""
        try:
            template = {
                "sections": [],
                "special_elements": {}
            }

            # Add sections from analysis
            for section in analysis.get("key_sections", []):
                template["sections"].append({
                    "name": section,
                    "type": "section",
                    "formatting": {
                        "style": "SectionHeading",
                        "spacing": 15
                    }
                })

            # Add default sections if none found
            if not template["sections"]:
                template["sections"] = [
                    {
                        "name": "GENERAL TERMS",
                        "type": "section",
                        "formatting": {
                            "style": "SectionHeading",
                            "spacing": 15
                        }
                    }
                ]

            return template

        except Exception as e:
            self.logger.error(f"Error generating template: {str(e)}")
            return {
                "sections": [
                    {
                        "name": "GENERAL TERMS",
                        "type": "section",
                        "formatting": {
                            "style": "SectionHeading",
                            "spacing": 15
                        }
                    }
                ],
                "special_elements": {}
            }
    def review_and_enhance_analysis(self, initial_analysis: Dict, contract_content: str) -> Dict:
        """
        Review and enhance the initial contract analysis using a secondary AI review.
        
        Args:
            initial_analysis (Dict): Initial AI analysis of the contract
            contract_content (str): Original contract content
            
        Returns:
            Dict: Enhanced and validated analysis
        """
        try:
            self.logger.info("Starting analysis review and enhancement...")
            
            # First, validate the initial analysis
            validation_result = self._validate_analysis(initial_analysis, contract_content)
            
            # Get AI recommendations for improvements
            improvements = self._get_ai_recommendations(initial_analysis, validation_result, contract_content)
            
            # Enhance readability
            readable_content = self._enhance_readability(contract_content)
            
            # Combine everything into enhanced analysis
            enhanced_analysis = self._combine_analysis(
                initial_analysis,
                validation_result,
                improvements,
                readable_content
            )
            
            self.logger.info("Analysis review and enhancement completed successfully")
            return enhanced_analysis
            
        except Exception as e:
            self.logger.error(f"Error in analysis review: {str(e)}")
            return initial_analysis

    def _validate_analysis(self, analysis: Dict, content: str) -> Dict:
        """Validate the initial analysis using a separate AI instance"""
        try:
            prompt = f"""Review this contract analysis for accuracy and completeness.
            
            Original Analysis:
            {json.dumps(analysis, indent=2)}

            Contract Content Sample:
            {content[:1500]}  # First 1500 chars to stay within token limits

            Evaluate:
            1. Are all required sections identified?
            2. Is the contract type correctly identified?
            3. Are all parties and roles clearly defined?
            4. Are all legal requirements covered?
            5. Are formatting requirements appropriate?

            Return a JSON object with:
            {{
                "validation_result": "pass/fail",
                "issues_found": [],
                "missing_elements": [],
                "suggested_improvements": [],
                "compliance_check": {{
                    "legal_requirements_met": boolean,
                    "missing_clauses": []
                }}
            }}
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a legal contract validation expert. Review contract analysis for accuracy and completeness."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            self.logger.error(f"Error in analysis validation: {str(e)}")
            return {
                "validation_result": "fail",
                "issues_found": ["Validation error occurred"],
                "missing_elements": [],
                "suggested_improvements": [],
                "compliance_check": {
                    "legal_requirements_met": False,
                    "missing_clauses": []
                }
            }

    def _get_ai_recommendations(self, analysis: Dict, validation: Dict, content: str) -> Dict:
        """Get AI recommendations for improvements"""
        try:
            prompt = f"""Review this contract and provide recommendations for improvements.
            
            Previous Analysis:
            {json.dumps(analysis, indent=2)}

            Validation Results:
            {json.dumps(validation, indent=2)}

            Focus on:
            1. Clarity and readability
            2. Legal completeness
            3. Structure and organization
            4. Language precision
            5. Risk coverage

            Provide recommendations in JSON format:
            {{
                "structural_improvements": [],
                "language_recommendations": [],
                "clarity_enhancements": [],
                "risk_mitigations": [],
                "additional_clauses": []
            }}
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a legal contract improvement specialist. Provide detailed recommendations for contract enhancement."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            self.logger.error(f"Error getting AI recommendations: {str(e)}")
            return {
                "structural_improvements": [],
                "language_recommendations": [],
                "clarity_enhancements": [],
                "risk_mitigations": [],
                "additional_clauses": []
            }

    def _enhance_readability(self, content: str) -> str:
        """Enhance contract readability by expanding abbreviations and improving language"""
        try:
            # Expand common abbreviations
            enhanced_content = content
            for abbr, full_form in self.common_abbreviations.items():
                # Only replace if it's a standalone abbreviation (not part of another word)
                enhanced_content = enhanced_content.replace(f" {abbr} ", f" {full_form} ({abbr}) ")

            # Use AI to further enhance readability
            prompt = f"""Improve the readability of this contract content while maintaining its legal validity.
            
            Original Content:
            {enhanced_content}

            Please:
            1. Use complete sentences instead of fragments
            2. Clarify technical terms
            3. Use consistent language
            4. Maintain formal tone
            5. Ensure clarity without losing legal precision
            
            Return the enhanced content with improved readability.
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a legal document clarity expert. Improve contract readability while maintaining legal precision."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"Error enhancing readability: {str(e)}")
            return content

    def _combine_analysis(self, 
                         initial_analysis: Dict, 
                         validation: Dict, 
                         improvements: Dict,
                         readable_content: str) -> Dict:
        """Combine all analyses into a comprehensive enhanced analysis"""
        try:
            enhanced_analysis = {
                **initial_analysis,
                "validation_results": validation,
                "improvement_recommendations": improvements,
                "enhanced_content": readable_content,
                "analysis_metadata": {
                    "version": "2.0",
                    "analysis_date": datetime.now().isoformat(),
                    "enhancement_applied": True,
                    "readability_improved": True
                },
                "quality_metrics": {
                    "readability_score": self._calculate_readability_score(readable_content),
                    "completeness_score": self._calculate_completeness_score(validation),
                    "clarity_score": self._calculate_clarity_score(readable_content)
                }
            }

            # Add section-specific enhancements
            enhanced_analysis["enhanced_sections"] = self._enhance_sections(
                initial_analysis.get("sections", []),
                improvements
            )

            return enhanced_analysis

        except Exception as e:
            self.logger.error(f"Error combining analysis: {str(e)}")
            return initial_analysis

    def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score for the content"""
        # Implement readability scoring logic (e.g., Flesch-Kincaid)
        try:
            # Simplified scoring for demonstration
            words = content.split()
            long_words = sum(1 for word in words if len(word) > 6)
            score = 1 - (long_words / len(words))
            return round(score * 100, 2)
        except:
            return 0.0

    def _calculate_completeness_score(self, validation: Dict) -> float:
        """Calculate completeness score based on validation results"""
        try:
            issues = len(validation.get("issues_found", []))
            missing = len(validation.get("missing_elements", []))
            base_score = 100
            deductions = (issues * 5) + (missing * 10)
            return max(0, min(100, base_score - deductions))
        except:
            return 0.0

    def _calculate_clarity_score(self, content: str) -> float:
        """Calculate clarity score for the content"""
        try:
            # Simple clarity scoring based on sentence length and structure
            sentences = content.split('.')
            avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
            clarity_score = 100 - (avg_length - 15 if avg_length > 15 else 0)
            return max(0, min(100, clarity_score))
        except:
            return 0.0

    def _enhance_sections(self, sections: List[Dict], improvements: Dict) -> List[Dict]:
        """Enhance individual sections based on improvements"""
        try:
            enhanced_sections = []
            for section in sections:
                enhanced_section = {
                    **section,
                    "improvements_applied": [],
                    "clarity_enhancements": []
                }

                # Apply relevant improvements
                for improvement in improvements.get("structural_improvements", []):
                    if improvement.get("section") == section.get("name"):
                        enhanced_section["improvements_applied"].append(improvement)

                # Apply clarity enhancements
                for enhancement in improvements.get("clarity_enhancements", []):
                    if enhancement.get("applicable_sections") is None or \
                       section.get("name") in enhancement.get("applicable_sections", []):
                        enhanced_section["clarity_enhancements"].append(enhancement)

                enhanced_sections.append(enhanced_section)

            return enhanced_sections

        except Exception as e:
            self.logger.error(f"Error enhancing sections: {str(e)}")
            return sections
