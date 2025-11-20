from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Task
from .forms import TaskForm, TaskFilterForm


@login_required
def task_list_view(request):
    """Display list of tasks with filtering options"""
    tasks = Task.objects.filter(
        Q(created_by=request.user) | Q(assigned_to=request.user)
    ).distinct()
    
    # Handle filtering
    filter_form = TaskFilterForm(request.GET)
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        priority = filter_form.cleaned_data.get('priority')
        show_completed = filter_form.cleaned_data.get('show_completed', True)
        assigned_to_me = filter_form.cleaned_data.get('assigned_to_me', False)
        
        if status:
            tasks = tasks.filter(status=status)
        
        if priority:
            tasks = tasks.filter(priority=priority)
        
        if not show_completed:
            tasks = tasks.filter(completed=False)
        
        if assigned_to_me:
            tasks = tasks.filter(assigned_to=request.user)
    
    # Order tasks: overdue first, then by deadline, then by created_at
    tasks = tasks.order_by('deadline', '-created_at')
    
    # Pagination
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tasks': page_obj,
        'filter_form': filter_form,
        'overdue_count': Task.objects.filter(
            Q(created_by=request.user) | Q(assigned_to=request.user),
            deadline__lt=timezone.now(),
            completed=False
        ).count(),
    }
    
    return render(request, 'todos/task_list.html', context)


@login_required
def task_create_view(request):
    """Create a new task"""
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            if not task.assigned_to:
                task.assigned_to = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('todos:task_list')
    else:
        form = TaskForm(user=request.user)
    
    return render(request, 'todos/task_form.html', {'form': form, 'action': 'Create'})


@login_required
def task_detail_view(request, pk):
    """View task details"""
    task = get_object_or_404(Task, pk=pk)
    
    # Check if user has permission to view this task
    if task.created_by != request.user and task.assigned_to != request.user:
        messages.error(request, 'You do not have permission to view this task.')
        return redirect('todos:task_list')
    
    return render(request, 'todos/task_detail.html', {'task': task})


@login_required
def task_update_view(request, pk):
    """Update an existing task"""
    task = get_object_or_404(Task, pk=pk)
    
    # Check if user has permission to edit this task
    if not task.can_be_edited_by(request.user):
        messages.error(request, 'You do not have permission to edit this task.')
        return redirect('todos:task_list')
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('todos:task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task, user=request.user)
    
    return render(request, 'todos/task_form.html', {'form': form, 'task': task, 'action': 'Update'})


@login_required
def task_delete_view(request, pk):
    """Delete a task"""
    task = get_object_or_404(Task, pk=pk)
    
    # Check if user has permission to delete this task
    if not task.can_be_deleted_by(request.user):
        messages.error(request, 'You do not have permission to delete this task.')
        return redirect('todos:task_list')
    
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect('todos:task_list')
    
    return render(request, 'todos/task_confirm_delete.html', {'task': task})


@login_required
def task_toggle_complete_view(request, pk):
    """Toggle task completion status"""
    task = get_object_or_404(Task, pk=pk)
    
    # Check if user has permission to modify this task
    if not task.can_be_edited_by(request.user):
        messages.error(request, 'You do not have permission to modify this task.')
        return redirect('todos:task_list')
    
    if task.completed:
        task.mark_as_pending()
        messages.success(request, f'Task "{task.title}" marked as pending.')
    else:
        task.mark_as_completed()
        messages.success(request, f'Task "{task.title}" marked as completed!')
    
    return redirect('todos:task_list')


