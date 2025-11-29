from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskSerializer, TaskAnalysisSerializer
from .scoring import TaskScorer
from .models import Task

@api_view(['POST'])
def analyze_tasks(request):
    """
    POST /api/tasks/analyze/
    
    Accept a list of tasks and return them sorted by priority score.
    
    Request body:
    {
        "tasks": [...],
        "strategy": "smart_balance"  # optional
    }
    """
    try:
        tasks_data = request.data.get('tasks', [])
        strategy = request.data.get('strategy', 'smart_balance')
        
        if not tasks_data:
            return Response(
                {'error': 'No tasks provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate tasks
        if not isinstance(tasks_data, list):
            return Response(
                {'error': 'Tasks must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initialize scorer with strategy
        try:
            scorer = TaskScorer(strategy=strategy)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Analyze tasks
        analyzed_tasks = scorer.analyze_tasks(tasks_data)
        
        response_data = {
            'tasks': analyzed_tasks,
            'strategy_used': strategy,
            'total_tasks': len(analyzed_tasks)
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'Error analyzing tasks: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST', 'GET'])
def suggest_tasks(request):
    """
    GET/POST /api/tasks/suggest/
    
    Return the top 3 tasks the user should work on today.
    
    For POST: Send tasks in request body
    For GET: Uses tasks from database (if any)
    """
    try:
        if request.method == 'POST':
            tasks_data = request.data.get('tasks', [])
            strategy = request.data.get('strategy', 'smart_balance')
        else:
            # For GET, use tasks from database
            tasks = Task.objects.all()
            serializer = TaskSerializer(tasks, many=True)
            tasks_data = serializer.data
            strategy = request.GET.get('strategy', 'smart_balance')
        
        if not tasks_data:
            return Response(
                {'message': 'No tasks available to suggest'},
                status=status.HTTP_200_OK
            )
        
        # Initialize scorer
        try:
            scorer = TaskScorer(strategy=strategy)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get top 3 suggestions
        top_tasks = scorer.get_top_suggestions(tasks_data, n=3)
        
        return Response({
            'suggestions': top_tasks,
            'strategy_used': strategy,
            'suggestion_count': len(top_tasks)
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'Error generating suggestions: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
def task_list_create(request):
    """
    GET /api/tasks/ - List all tasks
    POST /api/tasks/ - Create a new task
    """
    if request.method == 'GET':
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def task_detail(request, pk):
    """
    GET /api/tasks/<id>/ - Retrieve a task
    PUT /api/tasks/<id>/ - Update a task
    DELETE /api/tasks/<id>/ - Delete a task
    """
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response(
            {'error': 'Task not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
def clear_all_tasks(request):
    """
    DELETE /api/tasks/clear/ - Clear all tasks
    """
    count = Task.objects.count()
    Task.objects.all().delete()
    return Response({
        'message': f'Deleted {count} tasks',
        'deleted_count': count
    }, status=status.HTTP_200_OK)