import os
from typing import Dict, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

import logging


class ContractFormatter:
    """Handles contract formatting and style management"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.color_schemes = {
            'employment': {
                'primary': colors.HexColor('#000080'),
                'secondary': colors.HexColor('#4B4B4B'),
                'accent': colors.HexColor('#1E90FF')
            },
            'service': {
                'primary': colors.HexColor('#006400'),
                'secondary': colors.HexColor('#4B4B4B'),
                'accent': colors.HexColor('#32CD32')
            },
            'lease': {
                'primary': colors.HexColor('#8B4513'),
                'secondary': colors.HexColor('#4B4B4B'),
                'accent': colors.HexColor('#DEB887')
            },
            'nda': {
                'primary': colors.HexColor('#800000'),
                'secondary': colors.HexColor('#4B4B4B'),
                'accent': colors.HexColor('#DC143C')
            }
        }
        self.logger = logging.getLogger(__name__)

    def setup_styles(self, contract_type: str, formatting_requirements: Dict):
        """Setup styles based on contract type and requirements"""
        try:
            colors = self.color_schemes.get(contract_type, self.color_schemes['employment'])
            
            # Main title style
            self.styles.add(ParagraphStyle(
                name='ContractTitle',
                parent=self.styles['Heading1'],
                fontSize=16,
                alignment=TA_CENTER,
                spaceAfter=30,
                bold=True,
                textColor=colors['primary']
            ))

            # Section heading style
            self.styles.add(ParagraphStyle(
                name='SectionHeading',
                parent=self.styles['Heading2'],
                fontSize=12,
                spaceBefore=15,
                spaceAfter=10,
                bold=True,
                textColor=colors['primary'],
                keepWithNext=True
            ))

            # Subsection heading style
            self.styles.add(ParagraphStyle(
                name='SubsectionHeading',
                parent=self.styles['Heading3'],
                fontSize=11,
                spaceBefore=10,
                spaceAfter=8,
                bold=True,
                textColor=colors['secondary'],
                leftIndent=20
            ))

            # Normal text style
            self.styles.add(ParagraphStyle(
                name='NormalText',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=8,
                alignment=TA_JUSTIFY,
                textColor=colors['secondary']
            ))

            # List item style
            self.styles.add(ParagraphStyle(
                name='ListItem',
                parent=self.styles['Normal'],
                fontSize=10,
                leftIndent=20,
                spaceAfter=6,
                bulletIndent=10,
                textColor=colors['secondary']
            ))

            # Signature style
            self.styles.add(ParagraphStyle(
                name='Signature',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceBefore=30,
                spaceAfter=60,
                textColor=colors['primary']
            ))

            # Add custom styles from formatting requirements
            if formatting_requirements:
                for name, props in formatting_requirements.items():
                    self.styles.add(ParagraphStyle(
                        name=f'Custom_{name}',
                        parent=self.styles['Normal'],
                        **props
                    ))

            self.logger.info(f"Styles set up successfully for {contract_type} contract")

        except Exception as e:
            self.logger.error(f"Error setting up styles: {str(e)}")