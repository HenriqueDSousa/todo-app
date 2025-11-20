from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.contrib.messages import get_messages
import pytest
from todos.models import Task
from todos.forms import TaskForm, TaskFilterForm


@pytest.mark.unit
class TaskModelTestCase(TestCase):
    """Unit tests for Task model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
    
    def test_task_creation(self):
        """Test creating a task with minimal required fields"""
        task = Task.objects.create(
            title='Test Task',
            created_by=self.user,
            assigned_to=self.user
        )
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.created_by, self.user)
        self.assertEqual(task.assigned_to, self.user)
        self.assertFalse(task.completed)
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.priority, 'medium')
    
    def test_task_str_representation(self):
        """Test task string representation"""
        task = Task.objects.create(
            title='Test Task',
            created_by=self.user,
            assigned_to=self.user
        )
        self.assertIn('Test Task', str(task))
        self.assertIn('Pending', str(task))
    
    def test_task_with_all_fields(self):
        """Test creating a task with all fields"""
        deadline = timezone.now() + timedelta(days=7)
        task = Task.objects.create(
            title='Complete Task',
            description='This is a detailed description',
            deadline=deadline,
            priority='high',
            status='in_progress',
            created_by=self.user,
            assigned_to=self.other_user
        )
        self.assertEqual(task.title, 'Complete Task')
        self.assertEqual(task.description, 'This is a detailed description')
        self.assertEqual(task.priority, 'high')
        self.assertEqual(task.status, 'in_progress')
        self.assertEqual(task.assigned_to, self.other_user)
    
    def test_task_mark_as_completed(self):
        """Test marking a task as completed"""
        task = Task.objects.create(
            title='Test Task',
            created_by=self.user,
            assigned_to=self.user
        )
        self.assertFalse(task.completed)
        self.assertIsNone(task.completed_at)
        
        task.mark_as_completed()
        task.refresh_from_db()
        
        self.assertTrue(task.completed)
        self.assertEqual(task.status, 'completed')
        self.assertIsNotNone(task.completed_at)
    
    def test_task_mark_as_pending(self):
        """Test marking a completed task as pending"""
        task = Task.objects.create(
            title='Test Task',
            created_by=self.user,
            assigned_to=self.user,
            completed=True,
            completed_at=timezone.now()
        )
        
        task.mark_as_pending()
        task.refresh_from_db()
        
        self.assertFalse(task.completed)
        self.assertEqual(task.status, 'pending')
        self.assertIsNone(task.completed_at)
    
    def test_task_is_overdue(self):
        """Test checking if a task is overdue"""
        past_deadline = timezone.now() - timedelta(days=1)
        future_deadline = timezone.now() + timedelta(days=1)
        
        overdue_task = Task.objects.create(
            title='Overdue Task',
            created_by=self.user,
            assigned_to=self.user,
            deadline=past_deadline,
            completed=False
        )
        
        future_task = Task.objects.create(
            title='Future Task',
            created_by=self.user,
            assigned_to=self.user,
            deadline=future_deadline,
            completed=False
        )
        
        self.assertTrue(overdue_task.is_overdue())
        self.assertFalse(future_task.is_overdue())
    
    def test_task_is_not_overdue_when_completed(self):
        """Test that completed tasks are not considered overdue"""
        past_deadline = timezone.now() - timedelta(days=1)
        task = Task.objects.create(
            title='Completed Overdue Task',
            created_by=self.user,
            assigned_to=self.user,
            deadline=past_deadline,
            completed=True
        )
        
        self.assertFalse(task.is_overdue())
    
    def test_task_get_days_until_deadline(self):
        """Test getting days until deadline"""
        deadline = timezone.now() + timedelta(days=5)
        task = Task.objects.create(
            title='Test Task',
            created_by=self.user,
            assigned_to=self.user,
            deadline=deadline
        )
        
        days = task.get_days_until_deadline()
        self.assertIsNotNone(days)
        self.assertGreaterEqual(days, 4)
        self.assertLessEqual(days, 5)
    
    def test_task_get_days_until_deadline_without_deadline(self):
        """Test getting days until deadline when deadline is None"""
        task = Task.objects.create(
            title='Test Task',
            created_by=self.user,
            assigned_to=self.user
        )
        
        self.assertIsNone(task.get_days_until_deadline())
    
    def test_task_can_be_edited_by_creator(self):
        """Test that creator can edit task"""
        task = Task.objects.create(
            title='Test Task',
            created_by=self.user,
            assigned_to=self.user
        )
        
        self.assertTrue(task.can_be_edited_by(self.user))
    
    def test_task_can_be_edited_by_assigned_user(self):
        """Test that assigned user can edit task"""
        task = Task.objects.create(
            title='Test Task',
            created_by=self.user,
            assigned_to=self.other_user
        )
        
        self.assertTrue(task.can_be_edited_by(self.other_user))
    
    def test_task_cannot_be_edited_by_other_user(self):
        """Test that other users cannot edit task"""
        third_user = User.objects.create_user(
            username='thirduser',
            password='testpass123'
        )
        task = Task.objects.create(
            title='Test Task',
            created_by=self.user,
            assigned_to=self.user
        )
        
        self.assertFalse(task.can_be_edited_by(third_user))
    
    def test_task_can_be_deleted_by_creator(self):
        """Test that creator can delete task"""
        task = Task.objects.create(
            title='Test Task',
            created_by=self.user,
            assigned_to=self.user
        )
        
        self.assertTrue(task.can_be_deleted_by(self.user))
    
    def test_task_cannot_be_deleted_by_assigned_user(self):
        """Test that assigned user cannot delete task"""
        task = Task.objects.create(
            title='Test Task',
            created_by=self.user,
            assigned_to=self.other_user
        )
        
        self.assertFalse(task.can_be_deleted_by(self.other_user))
    
    def test_task_ordering(self):
        """Test that tasks are ordered by created_at descending"""
        task1 = Task.objects.create(
            title='First Task',
            created_by=self.user,
            assigned_to=self.user
        )
        task2 = Task.objects.create(
            title='Second Task',
            created_by=self.user,
            assigned_to=self.user
        )
        
        tasks = list(Task.objects.all())
        self.assertEqual(tasks[0], task2)
        self.assertEqual(tasks[1], task1)
    
    def test_task_clean_validates_past_deadline(self):
        """Test that clean method prevents past deadlines"""
        past_deadline = timezone.now() - timedelta(days=1)
        task = Task(
            title='Test Task',
            created_by=self.user,
            assigned_to=self.user,
            deadline=past_deadline
        )
        
        with self.assertRaises(Exception):
            task.clean()