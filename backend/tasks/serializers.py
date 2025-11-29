from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'due_date', 'estimated_hours', 'importance', 'dependencies']
    
    def validate_dependencies(self, value):
        """Ensure dependencies is a list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Dependencies must be a list")
        return value
    
    def validate_importance(self, value):
        """Ensure importance is between 1 and 10"""
        if value < 1 or value > 10:
            raise serializers.ValidationError("Importance must be between 1 and 10")
        return value
    
    def validate_estimated_hours(self, value):
        """Ensure estimated hours is positive"""
        if value <= 0:
            raise serializers.ValidationError("Estimated hours must be positive")
        return value


class TaskAnalysisSerializer(serializers.Serializer):
    """Serializer for analyzed task output"""
    id = serializers.IntegerField(required=False)
    title = serializers.CharField()
    due_date = serializers.DateField()
    estimated_hours = serializers.FloatField()
    importance = serializers.IntegerField()
    dependencies = serializers.ListField(child=serializers.IntegerField(), required=False)
    priority_score = serializers.FloatField(read_only=True)
    priority_level = serializers.CharField(read_only=True)
    explanation = serializers.CharField(read_only=True)
    breakdown = serializers.DictField(read_only=True)