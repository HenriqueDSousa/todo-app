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


@pytest.mark.unit
class TaskFormTestCase(TestCase):
    """Unit tests for TaskForm"""
    
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
    
    def test_task_form_valid_data(self):
        """Test TaskForm with valid data"""
        deadline = timezone.now() + timedelta(days=7)
        form_data = {
            'title': 'New Task',
            'description': 'Task description',
            'deadline': deadline.strftime('%Y-%m-%d %H:%M:%S'),
            'priority': 'high',
            'assigned_to': self.other_user.id
        }
        form = TaskForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_task_form_minimal_data(self):
        """Test TaskForm with minimal required data"""
        form_data = {
            'title': 'New Task',
        }
        form = TaskForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_task_form_rejects_past_deadline(self):
        """Test that TaskForm rejects past deadlines"""
        past_deadline = timezone.now() - timedelta(days=1)
        form_data = {
            'title': 'New Task',
            'deadline': past_deadline.strftime('%Y-%m-%d %H:%M:%S')
        }
        form = TaskForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('deadline', form.errors)
    
    def test_task_form_excludes_creator_from_assigned_to(self):
        """Test that creator is excluded from assigned_to queryset"""
        form = TaskForm(user=self.user)
        assigned_to_queryset = form.fields['assigned_to'].queryset
        self.assertNotIn(self.user, assigned_to_queryset)
        self.assertIn(self.other_user, assigned_to_queryset)
    
    def test_task_form_auto_assigns_to_creator_when_empty(self):
        """Test that form assigns task to creator when assigned_to is empty"""
        form_data = {
            'title': 'New Task',
        }
        form = TaskForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        task = form.save(commit=False)
        form.clean()
        self.assertEqual(task.assigned_to, self.user)


@pytest.mark.unit
class TaskViewTestCase(TestCase):
    """Unit tests for Task views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='Test description',
            created_by=self.user,
            assigned_to=self.user
        )
    
    def test_task_list_view_requires_login(self):
        """Test that task list view requires authentication"""
        response = self.client.get(reverse('todos:task_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_task_list_view_authenticated(self):
        """Test task list view for authenticated user"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('todos:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')
    
    def test_task_list_view_shows_user_tasks_only(self):
        """Test that task list only shows tasks for the logged-in user"""
        third_user = User.objects.create_user(
            username='thirduser',
            password='testpass123'
        )
        Task.objects.create(
            title='Other User Task',
            created_by=third_user,
            assigned_to=third_user
        )
        
        self.client.force_login(self.user)
        response = self.client.get(reverse('todos:task_list'))
        self.assertContains(response, 'Test Task')
        self.assertNotContains(response, 'Other User Task')
    
    def test_task_create_view_get(self):
        """Test GET request to task create view"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('todos:task_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create')
        self.assertContains(response, 'form')
    
    def test_task_create_view_post_valid(self):
        """Test POST request to create a task with valid data"""
        self.client.force_login(self.user)
        deadline = timezone.now() + timedelta(days=7)
        form_data = {
            'title': 'New Task',
            'description': 'New description',
            'deadline': deadline.strftime('%Y-%m-%d %H:%M:%S'),
            'priority': 'high'
        }
        response = self.client.post(reverse('todos:task_create'), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='New Task').exists())
    
    def test_task_detail_view(self):
        """Test task detail view"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('todos:task_detail', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')
        self.assertContains(response, 'Test description')
    
    def test_task_detail_view_permission(self):
        """Test that users can only view their own tasks"""
        third_user = User.objects.create_user(
            username='thirduser',
            password='testpass123'
        )
        other_task = Task.objects.create(
            title='Other Task',
            created_by=third_user,
            assigned_to=third_user
        )
        
        self.client.force_login(self.user)
        response = self.client.get(reverse('todos:task_detail', args=[other_task.pk]))
        self.assertEqual(response.status_code, 302)
    
    def test_task_update_view_get(self):
        """Test GET request to task update view"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('todos:task_update', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Update')
        self.assertContains(response, 'Test Task')
    
    def test_task_update_view_post(self):
        """Test POST request to update a task"""
        self.client.force_login(self.user)
        form_data = {
            'title': 'Updated Task',
            'description': 'Updated description',
            'priority': 'low'
        }
        response = self.client.post(reverse('todos:task_update', args=[self.task.pk]), form_data)
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')
    
    def test_task_update_view_permission(self):
        """Test that only creator or assigned user can update task"""
        third_user = User.objects.create_user(
            username='thirduser',
            password='testpass123'
        )
        self.client.force_login(third_user)
        response = self.client.get(reverse('todos:task_update', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
    
    def test_task_delete_view_get(self):
        """Test GET request to task delete view"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('todos:task_delete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete')
        self.assertContains(response, 'Test Task')
    
    def test_task_delete_view_post(self):
        """Test POST request to delete a task"""
        self.client.force_login(self.user)
        task_id = self.task.pk
        response = self.client.post(reverse('todos:task_delete', args=[task_id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=task_id).exists())
    
    def test_task_delete_view_permission(self):
        """Test that only creator can delete task"""
        task = Task.objects.create(
            title='Assigned Task',
            created_by=self.user,
            assigned_to=self.other_user
        )
        self.client.force_login(self.other_user)
        response = self.client.post(reverse('todos:task_delete', args=[task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())
    
    def test_task_toggle_complete_view(self):
        """Test toggling task completion status"""
        self.client.force_login(self.user)
        self.assertFalse(self.task.completed)
        
        response = self.client.post(reverse('todos:task_toggle_complete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)
        
        response = self.client.post(reverse('todos:task_toggle_complete', args=[self.task.pk]))
        self.task.refresh_from_db()
        self.assertFalse(self.task.completed)
    
    def test_task_list_filter_by_status(self):
        """Test filtering tasks by status"""
        Task.objects.create(
            title='Completed Task',
            created_by=self.user,
            assigned_to=self.user,
            status='completed',
            completed=True
        )
        
        self.client.force_login(self.user)
        response = self.client.get(reverse('todos:task_list'), {'status': 'completed'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Completed Task')
    
    def test_task_list_filter_by_priority(self):
        """Test filtering tasks by priority"""
        Task.objects.create(
            title='High Priority Task',
            created_by=self.user,
            assigned_to=self.user,
            priority='high'
        )
        
        self.client.force_login(self.user)
        response = self.client.get(reverse('todos:task_list'), {'priority': 'high'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'High Priority Task')
    
    def test_task_list_filter_hide_completed(self):
        """Test hiding completed tasks"""
        Task.objects.create(
            title='Completed Task',
            created_by=self.user,
            assigned_to=self.user,
            completed=True
        )
        
        self.client.force_login(self.user)
        response = self.client.get(reverse('todos:task_list'), {'show_completed': False})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Completed Task')
    
    def test_task_list_filter_assigned_to_me(self):
        """Test filtering tasks assigned to current user"""
        Task.objects.create(
            title='Assigned Task',
            created_by=self.user,
            assigned_to=self.other_user
        )
        
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('todos:task_list'), {'assigned_to_me': True})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Assigned Task')


@pytest.mark.unit
class TaskFilterFormTestCase(TestCase):
    """Unit tests for TaskFilterForm"""
    
    def test_task_filter_form_valid(self):
        """Test TaskFilterForm with valid data"""
        form_data = {
            'status': 'completed',
            'priority': 'high',
            'show_completed': True,
            'assigned_to_me': False
        }
        form = TaskFilterForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_task_filter_form_empty(self):
        """Test TaskFilterForm with empty data"""
        form = TaskFilterForm(data={})
        self.assertTrue(form.is_valid())


@pytest.mark.integration
class TaskIntegrationTestCase(TestCase):
    """Integration tests for complete task workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
    
    def test_complete_task_creation_workflow(self):
        """Integration test: Complete workflow from login to task creation"""
        # Step 1: Login
        self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Step 2: Navigate to task list
        response = self.client.get(reverse('todos:task_list'))
        self.assertEqual(response.status_code, 200)
        
        # Step 3: Create a new task
        deadline = timezone.now() + timedelta(days=7)
        response = self.client.post(reverse('todos:task_create'), {
            'title': 'Integration Test Task',
            'description': 'This is an integration test',
            'deadline': deadline.strftime('%Y-%m-%d %H:%M:%S'),
            'priority': 'high'
        })
        self.assertEqual(response.status_code, 302)
        
        # Step 4: Verify task was created
        task = Task.objects.get(title='Integration Test Task')
        self.assertEqual(task.created_by, self.user)
        self.assertEqual(task.assigned_to, self.user)
        
        # Step 5: View task detail
        response = self.client.get(reverse('todos:task_detail', args=[task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Test Task')
        
        # Step 6: Update task
        response = self.client.post(reverse('todos:task_update', args=[task.pk]), {
            'title': 'Updated Integration Task',
            'description': 'Updated description',
            'priority': 'medium'
        })
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Integration Task')
        
        # Step 7: Mark as completed
        response = self.client.post(reverse('todos:task_toggle_complete', args=[task.pk]))
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertTrue(task.completed)
        
        # Step 8: Delete task
        response = self.client.post(reverse('todos:task_delete', args=[task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())
    
    def test_task_assignment_workflow(self):
        """Integration test: Create task and assign to another user"""
        self.client.force_login(self.user)
        
        # Create task assigned to other user
        response = self.client.post(reverse('todos:task_create'), {
            'title': 'Assigned Task',
            'description': 'Task for other user',
            'priority': 'high',
            'assigned_to': self.other_user.id
        })
        self.assertEqual(response.status_code, 302)
        
        task = Task.objects.get(title='Assigned Task')
        self.assertEqual(task.assigned_to, self.other_user)
        self.assertEqual(task.created_by, self.user)
        
        # Other user can view and edit the task
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('todos:task_detail', args=[task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Assigned Task')
        
        # Other user can update the task
        response = self.client.post(reverse('todos:task_update', args=[task.pk]), {
            'title': 'Updated Assigned Task',
            'priority': 'medium'
        })
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Assigned Task')
        
        # Other user cannot delete the task
        response = self.client.post(reverse('todos:task_delete', args=[task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())
    
    def test_task_filtering_and_pagination_workflow(self):
        """Integration test: Create multiple tasks and test filtering"""
        self.client.force_login(self.user)
        
        # Create multiple tasks with different properties
        Task.objects.create(
            title='High Priority Task',
            created_by=self.user,
            assigned_to=self.user,
            priority='high',
            status='pending'
        )
        Task.objects.create(
            title='Completed Task',
            created_by=self.user,
            assigned_to=self.user,
            priority='medium',
            status='completed',
            completed=True
        )
        Task.objects.create(
            title='Low Priority Task',
            created_by=self.user,
            assigned_to=self.user,
            priority='low',
            status='in_progress'
        )
        
        # Test filtering by priority
        response = self.client.get(reverse('todos:task_list'), {'priority': 'high'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'High Priority Task')
        self.assertNotContains(response, 'Low Priority Task')
        
        # Test filtering by status
        response = self.client.get(reverse('todos:task_list'), {'status': 'completed'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Completed Task')
        
        # Test hiding completed tasks
        response = self.client.get(reverse('todos:task_list'), {'show_completed': False})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Completed Task')
    
    def test_task_permissions_workflow(self):
        """Integration test: Test task permissions across different users"""
        self.client.force_login(self.user)
        
        # Create task assigned to other user
        task = Task.objects.create(
            title='Permission Test Task',
            created_by=self.user,
            assigned_to=self.other_user
        )
        
        # Creator can view, edit, and delete
        response = self.client.get(reverse('todos:task_detail', args=[task.pk]))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('todos:task_update', args=[task.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Assigned user can view and edit but not delete
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('todos:task_detail', args=[task.pk]))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('todos:task_update', args=[task.pk]))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('todos:task_delete', args=[task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())
        
        # Third user cannot access
        third_user = User.objects.create_user(
            username='thirduser',
            password='testpass123'
        )
        self.client.force_login(third_user)
        response = self.client.get(reverse('todos:task_detail', args=[task.pk]))
        self.assertEqual(response.status_code, 302)
    
    def test_task_deadline_and_overdue_workflow(self):
        """Integration test: Test task deadlines and overdue functionality"""
        self.client.force_login(self.user)
        
        # Create task with future deadline
        future_deadline = timezone.now() + timedelta(days=5)
        future_task = Task.objects.create(
            title='Future Task',
            created_by=self.user,
            assigned_to=self.user,
            deadline=future_deadline
        )
        
        # Create task with past deadline (overdue)
        past_deadline = timezone.now() - timedelta(days=1)
        overdue_task = Task.objects.create(
            title='Overdue Task',
            created_by=self.user,
            assigned_to=self.user,
            deadline=past_deadline,
            completed=False
        )
        
        # View task list and check overdue count
        response = self.client.get(reverse('todos:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'overdue')
        
        # Verify overdue status
        self.assertFalse(future_task.is_overdue())
        self.assertTrue(overdue_task.is_overdue())
        
        # Complete overdue task
        response = self.client.post(reverse('todos:task_toggle_complete', args=[overdue_task.pk]))
        self.assertEqual(response.status_code, 302)
        overdue_task.refresh_from_db()
        self.assertTrue(overdue_task.completed)
        self.assertFalse(overdue_task.is_overdue())

