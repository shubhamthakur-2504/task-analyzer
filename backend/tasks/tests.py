from django.test import TestCase
from datetime import date, timedelta
from .scoring import TaskScorer

class TaskScorerTests(TestCase):
    """Unit tests for the TaskScorer algorithm"""
    
    def setUp(self):
        """Set up test data"""
        self.today = date.today()
        self.scorer = TaskScorer(strategy='smart_balance', today=self.today)
    
    def test_urgency_score_overdue_task(self):
        """Test that overdue tasks get high urgency scores"""
        overdue_date = self.today - timedelta(days=2)
        score = self.scorer.calculate_urgency_score(overdue_date)
        self.assertGreaterEqual(score, 100)
        self.assertEqual(score, 110)  # 100 + 2*5
    
    def test_urgency_score_due_today(self):
        """Test that tasks due today get high urgency"""
        score = self.scorer.calculate_urgency_score(self.today)
        self.assertEqual(score, 95)
    
    def test_urgency_score_due_tomorrow(self):
        """Test tasks due tomorrow"""
        tomorrow = self.today + timedelta(days=1)
        score = self.scorer.calculate_urgency_score(tomorrow)
        self.assertEqual(score, 90)
    
    def test_urgency_score_far_future(self):
        """Test tasks due far in the future"""
        far_future = self.today + timedelta(days=30)
        score = self.scorer.calculate_urgency_score(far_future)
        self.assertEqual(score, 10)
    
    def test_importance_score_conversion(self):
        """Test importance score conversion to 0-100 scale"""
        self.assertEqual(self.scorer.calculate_importance_score(1), 10)
        self.assertEqual(self.scorer.calculate_importance_score(5), 50)
        self.assertEqual(self.scorer.calculate_importance_score(10), 100)
    
    def test_effort_score_quick_wins(self):
        """Test that low effort tasks get higher scores"""
        low_effort_score = self.scorer.calculate_effort_score(1)
        high_effort_score = self.scorer.calculate_effort_score(10)
        self.assertGreater(low_effort_score, high_effort_score)
    
    def test_effort_score_zero_hours_handling(self):
        """Test handling of edge case with very low hours"""
        score = self.scorer.calculate_effort_score(0.1)
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_calculate_score_with_valid_task(self):
        """Test score calculation with a valid task"""
        task = {
            'id': 1,
            'title': 'Test Task',
            'due_date': self.today + timedelta(days=1),
            'estimated_hours': 2,
            'importance': 8,
            'dependencies': []
        }
        
        result = self.scorer.calculate_score(task)
        
        self.assertIn('priority_score', result)
        self.assertIn('priority_level', result)
        self.assertIn('explanation', result)
        self.assertIn('breakdown', result)
        self.assertGreater(result['priority_score'], 0)
    
    def test_calculate_score_with_invalid_data(self):
        """Test handling of invalid task data"""
        task = {
            'title': 'Invalid Task',
            'due_date': 'invalid-date',
            'estimated_hours': 'not-a-number',
            'importance': 5
        }
        
        result = self.scorer.calculate_score(task)
        
        self.assertEqual(result['priority_score'], 0)
        self.assertEqual(result['priority_level'], 'Low')
        self.assertIn('Invalid task data', result['explanation'])
    
    def test_calculate_score_high_priority_task(self):
        """Test that urgent, important tasks get high scores"""
        task = {
            'id': 1,
            'title': 'Urgent Important Task',
            'due_date': self.today,
            'estimated_hours': 1,
            'importance': 10,
            'dependencies': []
        }
        
        result = self.scorer.calculate_score(task)
        
        self.assertGreaterEqual(result['priority_score'], 80)
        self.assertEqual(result['priority_level'], 'High')
    
    def test_analyze_tasks_sorting(self):
        """Test that analyze_tasks returns sorted list"""
        tasks = [
            {
                'id': 1,
                'title': 'Low Priority',
                'due_date': self.today + timedelta(days=30),
                'estimated_hours': 10,
                'importance': 2,
                'dependencies': []
            },
            {
                'id': 2,
                'title': 'High Priority',
                'due_date': self.today,
                'estimated_hours': 1,
                'importance': 10,
                'dependencies': []
            },
            {
                'id': 3,
                'title': 'Medium Priority',
                'due_date': self.today + timedelta(days=7),
                'estimated_hours': 5,
                'importance': 5,
                'dependencies': []
            }
        ]
        
        analyzed = self.scorer.analyze_tasks(tasks)
        
        # Check that tasks are sorted by priority_score descending
        self.assertEqual(len(analyzed), 3)
        self.assertGreaterEqual(
            analyzed[0]['priority_score'],
            analyzed[1]['priority_score']
        )
        self.assertGreaterEqual(
            analyzed[1]['priority_score'],
            analyzed[2]['priority_score']
        )
        self.assertEqual(analyzed[0]['title'], 'High Priority')
    
    def test_get_top_suggestions(self):
        """Test getting top N suggestions"""
        tasks = [
            {
                'id': i,
                'title': f'Task {i}',
                'due_date': self.today + timedelta(days=i),
                'estimated_hours': i,
                'importance': 10 - i,
                'dependencies': []
            }
            for i in range(1, 6)
        ]
        
        suggestions = self.scorer.get_top_suggestions(tasks, n=3)
        
        self.assertEqual(len(suggestions), 3)
        # First task should have highest score
        self.assertGreaterEqual(
            suggestions[0]['priority_score'],
            suggestions[1]['priority_score']
        )
    
    
    def test_different_strategies(self):
        """Test that different strategies produce different scores"""
        task = {
            'id': 1,
            'title': 'Test Task',
            'due_date': self.today + timedelta(days=7),
            'estimated_hours': 5,
            'importance': 7,
            'dependencies': []
        }
        
        strategies = ['smart_balance', 'fastest_wins', 'high_impact', 'deadline_driven']
        scores = {}
        
        for strategy in strategies:
            scorer = TaskScorer(strategy=strategy)
            result = scorer.calculate_score(task)
            scores[strategy] = result['priority_score']
        
        # Scores should differ based on strategy
        # At least some strategies should produce different scores
        unique_scores = len(set(scores.values()))
        self.assertGreater(unique_scores, 1)
    
    def test_invalid_strategy_raises_error(self):
        """Test that invalid strategy raises ValueError"""
        with self.assertRaises(ValueError):
            TaskScorer(strategy='invalid_strategy')
    
    def test_explanation_generation(self):
        """Test that explanations are generated correctly"""
        task = {
            'id': 1,
            'title': 'Quick Important Task',
            'due_date': self.today,
            'estimated_hours': 1,
            'importance': 9,
            'dependencies': []
        }
        
        result = self.scorer.calculate_score(task)
        explanation = result['explanation']
        
        self.assertIn('Due today', explanation)
        self.assertIn('High importance', explanation)
        self.assertIn('Quick win', explanation)