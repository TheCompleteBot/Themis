# agents/feedback_loop_agent.py
from libraries import *
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid

@dataclass
class Feedback:
    """Data structure for feedback entries"""
    feedback_id: str = str(uuid.uuid4())
    source_type: str  # 'user' or 'expert'
    category: str
    content: str
    rating: Optional[int] = None
    context: Dict = None
    timestamp: datetime = datetime.now()
    status: str = 'pending'

class FeedbackLoopAgent:
    """
    Feedback Loop Agent for system improvement through feedback collection and processing.
    Handles feedback from users and experts to continuously improve the system.
    """
    def __init__(self, llm: OpenAI = None):
        self.logger = logging.getLogger(__name__)
        self.llm = llm or OpenAI(temperature=0.2)
        self.feedback_store = []
        self.learning_history = []

    def collect_feedback(
        self,
        source_id: str,
        feedback_data: Dict,
        source_type: str = 'user'
    ) -> Dict:
        """
        Collect feedback from users or experts.
        
        Args:
            source_id (str): Identifier for feedback source
            feedback_data (Dict): Feedback content and metadata
            source_type (str): Type of feedback source ('user' or 'expert')
            
        Returns:
            Dict: Feedback receipt confirmation
        """
        try:
            feedback = Feedback(
                source_type=source_type,
                category=feedback_data.get('category', 'general'),
                content=feedback_data.get('content', ''),
                rating=feedback_data.get('rating'),
                context={
                    'source_id': source_id,
                    'contract_id': feedback_data.get('contract_id'),
                    'contract_type': feedback_data.get('contract_type')
                }
            )
            
            self.feedback_store.append(feedback)
            
            # Process feedback immediately if from expert
            if source_type == 'expert':
                self._process_expert_feedback(feedback)
            
            return {
                'feedback_id': feedback.feedback_id,
                'status': 'received',
                'timestamp': feedback.timestamp.isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error collecting feedback: {str(e)}")
            raise

    def process_feedback_batch(self, batch_size: int = 100) -> Dict:
        """
        Process a batch of pending feedback.
        
        Args:
            batch_size (int): Number of feedback items to process
            
        Returns:
            Dict: Processing results and insights
        """
        try:
            pending = [f for f in self.feedback_store if f.status == 'pending'][:batch_size]
            results = {
                'processed': 0,
                'insights': [],
                'updates': []
            }
            
            for feedback in pending:
                insight = self._process_feedback(feedback)
                results['insights'].append(insight)
                feedback.status = 'processed'
                results['processed'] += 1
            
            self._update_learning_history(results['insights'])
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing feedback batch: {str(e)}")
            raise

    def get_feedback_analytics(self, time_period: Optional[str] = None) -> Dict:
        """
        Generate analytics from collected feedback.
        
        Args:
            time_period (str, optional): Time period for analysis
            
        Returns:
            Dict: Analytics results
        """
        try:
            analytics = {
                'total_feedback': len(self.feedback_store),
                'by_source': self._analyze_by_source(),
                'by_category': self._analyze_by_category(),
                'satisfaction_metrics': self._calculate_satisfaction_metrics(),
                'trending_issues': self._identify_trending_issues(),
                'improvement_areas': self._identify_improvement_areas()
            }
            
            if time_period:
                analytics['trends'] = self._analyze_trends(time_period)
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error generating analytics: {str(e)}")
            raise

    def _process_expert_feedback(self, feedback: Feedback) -> None:
        """Process feedback from legal experts."""
        try:
            # Extract key points
            key_points = self._extract_key_points(feedback.content)
            
            # Generate immediate actions
            actions = self._generate_expert_actions(key_points)
            
            # Update learning history
            self._update_learning_history([{
                'source': 'expert',
                'key_points': key_points,
                'actions': actions,
                'priority': 'high'
            }])
            
        except Exception as e:
            self.logger.error(f"Error processing expert feedback: {str(e)}")
            raise

    def _process_feedback(self, feedback: Feedback) -> Dict:
        """Process individual feedback entry."""
        try:
            # Extract key points from feedback
            key_points = self._extract_key_points(feedback.content)
            
            # Generate insights
            insights = self._generate_insights(key_points, feedback.context)
            
            # Prioritize actionable items
            actions = self._prioritize_actions(insights)
            
            return {
                'feedback_id': feedback.feedback_id,
                'key_points': key_points,
                'insights': insights,
                'actions': actions
            }
            
        except Exception as e:
            self.logger.error(f"Error processing feedback: {str(e)}")
            raise

    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from feedback content."""
        try:
            # Use LLM to extract key points
            prompt = f"Extract key points from this feedback: {content}"
            response = self.llm(prompt)
            
            # Process and clean the response
            key_points = [
                point.strip()
                for point in response.split('\n')
                if point.strip()
            ]
            
            return key_points
            
        except Exception as e:
            self.logger.error(f"Error extracting key points: {str(e)}")
            return []

    def _generate_insights(self, key_points: List[str], context: Dict) -> List[Dict]:
        """Generate insights from key points."""
        insights = []
        try:
            for point in key_points:
                prompt = f"Generate insight from this feedback point: {point}"
                response = self.llm(prompt)
                
                insights.append({
                    'point': point,
                    'insight': response,
                    'context': context,
                    'timestamp': datetime.now().isoformat()
                })
                
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {str(e)}")
            return insights

    def _update_learning_history(self, insights: List[Dict]) -> None:
        """Update learning history with new insights."""
        try:
            for insight in insights:
                self.learning_history.append({
                    'timestamp': datetime.now(),
                    'insight': insight,
                    'status': 'pending_implementation'
                })
                
        except Exception as e:
            self.logger.error(f"Error updating learning history: {str(e)}")
            raise

    def get_improvement_summary(self) -> Dict:
        """Generate summary of improvements based on feedback."""
        try:
            return {
                'total_feedback_processed': len(self.feedback_store),
                'improvements_implemented': len([
                    h for h in self.learning_history
                    if h['status'] == 'implemented'
                ]),
                'key_improvements': self._identify_key_improvements(),
                'pending_actions': self._get_pending_actions()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating improvement summary: {str(e)}")
            raise