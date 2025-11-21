from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


class Task(models.Model):
    """Task model representing a todo item"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    title = models.CharField(max_length=200, help_text="Task title")
    description = models.TextField(blank=True, help_text="Detailed task description")
    deadline = models.DateTimeField(null=True, blank=True, help_text="Task deadline")
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Task priority level"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Task status"
    )
    completed = models.BooleanField(default=False, help_text="Whether task is completed")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="When task was completed")
    
    # User relationships
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        help_text="User who created the task"
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        null=True,
        blank=True,
        help_text="User assigned to complete the task"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        indexes = [
            models.Index(fields=['created_by', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['deadline']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def clean(self):
        """Validate task data"""
        # Only validate deadline on creation (when pk is None)
        # Allow past deadlines for existing tasks (they might have been created in the past)
        if self.deadline and self.deadline < timezone.now() and self.pk is None:
            raise ValidationError("Deadline cannot be in the past")
        
        if self.completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.completed and self.completed_at:
            self.completed_at = None
    
    def save(self, *args, **kwargs):
        """Override save to ensure clean is called"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def mark_as_completed(self):
        """Mark task as completed"""
        self.completed = True
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_as_pending(self):
        """Mark task as pending"""
        self.completed = False
        self.status = 'pending'
        self.completed_at = None
        self.save()
    
    def is_overdue(self):
        """Check if task is overdue"""
        if self.deadline and not self.completed:
            return timezone.now() > self.deadline
        return False
    
    def get_days_until_deadline(self):
        """Get number of days until deadline"""
        if self.deadline:
            delta = self.deadline - timezone.now()
            return delta.days
        return None
    
    def can_be_edited_by(self, user):
        """Check if user can edit this task"""
        return self.created_by == user or self.assigned_to == user
    
    def can_be_deleted_by(self, user):
        """Check if user can delete this task"""
        return self.created_by == user


