from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'assigned_to', 'status', 'priority', 'deadline', 'completed', 'created_at']
    list_filter = ['status', 'priority', 'completed', 'created_at', 'deadline']
    search_fields = ['title', 'description', 'created_by__username', 'assigned_to__username']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'priority', 'status')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Timing', {
            'fields': ('deadline', 'completed', 'completed_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


