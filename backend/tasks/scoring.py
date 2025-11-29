from datetime import date, datetime
from typing import Dict, List, Any

class TaskScorer:
    """
    Smart Task Priority Scoring Algorithm
    
    This algorithm calculates task priority based on four main factors:
    1. Urgency - How soon is the task due?
    2. Importance - User-provided rating (1-10)
    3. Effort - Estimated hours (lower effort = quick wins)
    4. Dependencies - Tasks blocking others get higher priority
    
    The algorithm supports multiple strategies:
    - Smart Balance: Balanced weighting of all factors
    - Fastest Wins: Prioritizes low-effort tasks
    - High Impact: Prioritizes importance
    - Deadline Driven: Prioritizes due dates
    """
    
    # Strategy weights: (urgency, importance, effort, dependency_multiplier)
    STRATEGIES = {
        'smart_balance': (0.40, 0.35, 0.20, 1.0),
        'fastest_wins': (0.20, 0.10, 0.60, 0.5),
        'high_impact': (0.20, 0.60, 0.10, 0.5),
        'deadline_driven': (0.60, 0.25, 0.10, 0.3),
    }
    
    def __init__(self, strategy: str = 'smart_balance', today: date = None):
        """Initialize scorer with a strategy"""
        self.strategy = strategy
        if strategy not in self.STRATEGIES:
            raise ValueError(f"Invalid strategy. Choose from: {list(self.STRATEGIES.keys())}")
        self.today = today if today else date.today()
    
    def calculate_urgency_score(self, due_date: date) -> float:
        """
        Calculate urgency score based on days until due date.
        
        Returns: Score from 0-100 (higher = more urgent)
        - Overdue tasks get 100+ with penalty
        - Due today: 95
        - Due tomorrow: 90
        - Due in 2-3 days: 75
        - Due in 4-7 days: 50
        - Due in 8-14 days: 30
        - Due in 15+ days: 10
        """
        today = self.today
        delta = (due_date - today).days
        
        if delta < 0:
            # Overdue: base 100 + 5 points per day overdue (capped at 150)
            return min(100 + abs(delta) * 5, 150)
        elif delta == 0:
            return 95
        elif delta == 1:
            return 90
        elif delta <= 3:
            return 75
        elif delta <= 7:
            return 50
        elif delta <= 14:
            return 30
        else:
            return 10
    
    def calculate_importance_score(self, importance: int) -> float:
        """
        Convert importance (1-10) to 0-100 scale.
        """
        return importance * 10
    
    def calculate_effort_score(self, estimated_hours: float) -> float:
        """
        Calculate effort score (inverse relationship).
        Lower effort = higher score (quick wins).
        
        Returns: Score from 0-100
        """
        # Inverse relationship: 1/(hours) * 100, capped at 100
        # Add 0.5 to denominator to avoid division by zero and extreme values
        return min(100 / (estimated_hours + 0.5), 100)
    
    def calculate_dependency_boost(self, dependencies: List[int], all_tasks: List[Dict]) -> float:
        """
        Calculate boost based on how many tasks depend on this one.
        
        Returns: Additional points (0-50)
        """
        # Count how many OTHER tasks list this task as a dependency
        task_ids = {task.get('id') for task in all_tasks if task.get('id')}
        dependent_count = 0
        
        for task in all_tasks:
            task_deps = task.get('dependencies', [])
            if any(dep in task_ids for dep in task_deps):
                dependent_count += 1
        
        # Each dependent task adds 15 points, capped at 50
        return min(dependent_count * 15, 50)
    
    def calculate_score(self, task: Dict, all_tasks: List[Dict] = None) -> Dict[str, Any]:
        """
        Calculate priority score for a task.
        
        Args:
            task: Task dictionary with required fields
            all_tasks: List of all tasks (for dependency calculation)
        
        Returns:
            Dictionary with score, breakdown, and explanation
        """
        if all_tasks is None:
            all_tasks = [task]
        
        # Handle missing or invalid data
        try:
            due_date = task.get('due_date')
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            
            estimated_hours = float(task.get('estimated_hours', 1))
            importance = int(task.get('importance', 5))
            dependencies = task.get('dependencies', [])
            
        except (ValueError, TypeError) as e:
            # Return default low score for invalid data
            return {
                'priority_score': 0,
                'priority_level': 'Low',
                'explanation': f'Invalid task data: {str(e)}',
                'breakdown': {}
            }
        
        # Calculate component scores
        urgency_score = self.calculate_urgency_score(due_date)
        importance_score = self.calculate_importance_score(importance)
        effort_score = self.calculate_effort_score(estimated_hours)
        dependency_boost = self.calculate_dependency_boost(dependencies, all_tasks)
        
        # Get strategy weights
        urgency_weight, importance_weight, effort_weight, dep_multiplier = self.STRATEGIES[self.strategy]
        
        # Calculate final weighted score
        base_score = (
            urgency_score * urgency_weight +
            importance_score * importance_weight +
            effort_score * effort_weight
        )
        
        final_score = base_score + (dependency_boost * dep_multiplier)
        
        # Determine priority level
        if final_score >= 80:
            priority_level = 'High'
        elif final_score >= 50:
            priority_level = 'Medium'
        else:
            priority_level = 'Low'
        
        # Generate explanation
        explanation = self._generate_explanation(
            task, urgency_score, importance_score, effort_score, dependency_boost
        )
        
        return {
            'priority_score': round(final_score, 2),
            'priority_level': priority_level,
            'explanation': explanation,
            'breakdown': {
                'urgency': round(urgency_score, 2),
                'importance': round(importance_score, 2),
                'effort': round(effort_score, 2),
                'dependency_boost': round(dependency_boost, 2)
            }
        }
    
    def _generate_explanation(self, task: Dict, urgency: float, importance: float, 
                            effort: float, dep_boost: float) -> str:
        """Generate human-readable explanation for the score"""
        reasons = []
        
        # Check urgency
        due_date = task.get('due_date')
        if isinstance(due_date, str):
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        days_until = (due_date - self.today).days
        
        if days_until < 0:
            reasons.append(f"Overdue by {abs(days_until)} day(s)")
        elif days_until == 0:
            reasons.append("Due today")
        elif days_until == 1:
            reasons.append("Due tomorrow")
        elif days_until <= 3:
            reasons.append("Due very soon")
        
        # Check importance
        if task.get('importance', 0) >= 8:
            reasons.append("High importance rating")
        
        # Check effort
        if task.get('estimated_hours', 0) <= 2:
            reasons.append("Quick win (low effort)")
        
        # Check dependencies
        dep_count = len(task.get('dependencies', []))
        if dep_count > 0:
            reasons.append(f"Blocks {dep_count} other task(s)")
        
        if not reasons:
            reasons.append("Standard priority task")
        
        return " • ".join(reasons)
    
    def analyze_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """
        Analyze and sort all tasks by priority.
        
        Returns: Sorted list of tasks with scores
        """
        analyzed_tasks = []
        
        for task in tasks:
            score_data = self.calculate_score(task, tasks)
            analyzed_task = {**task, **score_data}
            analyzed_tasks.append(analyzed_task)
        
        # Sort by priority score (descending)
        analyzed_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return analyzed_tasks
    
    def get_top_suggestions(self, tasks: List[Dict], n: int = 3) -> List[Dict]:
        """
        Get top N task suggestions.
        
        Returns: Top N tasks with detailed explanations
        """
        analyzed = self.analyze_tasks(tasks)
        return analyzed[:n]