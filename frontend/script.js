// API Base URL
const API_BASE = 'http://localhost:8000/api/tasks';

// State management
let currentTasks = [];

// DOM Elements
const taskForm = document.getElementById('task-form');
const jsonInput = document.getElementById('json-input');
const loadJsonBtn = document.getElementById('load-json-btn');
const analyzeBtn = document.getElementById('analyze-btn');
const suggestBtn = document.getElementById('suggest-btn');
const clearBtn = document.getElementById('clear-btn');
const strategySelect = document.getElementById('strategy');
const importanceSlider = document.getElementById('importance');
const importanceValue = document.getElementById('importance-value');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('error-message');
const resultsContainer = document.getElementById('results-container');
const tasksContainer = document.getElementById('tasks-container');
const tasksList = document.getElementById('tasks-list');
const suggestionsContainer = document.getElementById('suggestions-container');
const suggestionsList = document.getElementById('suggestions-list');
const currentTasksList = document.getElementById('current-tasks-list');
const taskCount = document.getElementById('task-count');
const strategyDescription = document.getElementById('strategy-description');

// Strategy descriptions
const strategyDescriptions = {
    'smart_balance': 'Balanced weighting of urgency, importance, effort, and dependencies',
    'fastest_wins': 'Prioritizes low-effort tasks for quick wins',
    'high_impact': 'Focuses on high-importance tasks regardless of effort',
    'deadline_driven': 'Prioritizes tasks based on due dates'
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateStrategyDescription();
    updateCurrentTasksList();
    setDefaultDate();
});

// Set default date to today
function setDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('due_date').value = today;
}

// Update importance value display
importanceSlider.addEventListener('input', (e) => {
    importanceValue.textContent = e.target.value;
});

// Update strategy description
strategySelect.addEventListener('change', updateStrategyDescription);

function updateStrategyDescription() {
    const strategy = strategySelect.value;
    strategyDescription.textContent = strategyDescriptions[strategy];
}

// Add task from form
taskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const task = {
        id: Date.now(),
        title: document.getElementById('title').value,
        due_date: document.getElementById('due_date').value,
        estimated_hours: parseFloat(document.getElementById('estimated_hours').value),
        importance: parseInt(document.getElementById('importance').value),
        dependencies: parseDependencies(document.getElementById('dependencies').value)
    };
    
    // Validate
    if (!validateTask(task)) {
        return;
    }
    
    currentTasks.push(task);
    updateCurrentTasksList();
    taskForm.reset();
    setDefaultDate();
    importanceSlider.value = 5;
    importanceValue.textContent = '5';
    
    showSuccessMessage('Task added successfully!');
});

// Parse dependencies
function parseDependencies(input) {
    if (!input.trim()) return [];
    return input.split(',').map(d => parseInt(d.trim())).filter(d => !isNaN(d));
}

// Validate task
function validateTask(task) {
    if (!task.title.trim()) {
        showError('Task title is required');
        return false;
    }
    
    if (!task.due_date) {
        showError('Due date is required');
        return false;
    }
    
    if (task.estimated_hours <= 0) {
        showError('Estimated hours must be greater than 0');
        return false;
    }
    
    if (task.importance < 1 || task.importance > 10) {
        showError('Importance must be between 1 and 10');
        return false;
    }
    
    return true;
}

// Load tasks from JSON
loadJsonBtn.addEventListener('click', () => {
    try {
        const input = jsonInput.value.trim();
        if (!input) {
            showError('Please enter JSON data');
            return;
        }
        
        const tasks = JSON.parse(input);
        
        if (!Array.isArray(tasks)) {
            showError('JSON must be an array of tasks');
            return;
        }
        
        // Validate and add tasks
        let addedCount = 0;
        tasks.forEach(task => {
            if (validateTask(task)) {
                task.id = task.id || Date.now() + addedCount;
                currentTasks.push(task);
                addedCount++;
            }
        });
        
        if (addedCount > 0) {
            updateCurrentTasksList();
            jsonInput.value = '';
            showSuccessMessage(`${addedCount} task(s) loaded from JSON`);
        }
    } catch (error) {
        showError('Invalid JSON format: ' + error.message);
    }
});

// Analyze tasks
analyzeBtn.addEventListener('click', async () => {
    if (currentTasks.length === 0) {
        showError('Please add at least one task');
        return;
    }
    
    showLoading(true);
    hideError();
    
    try {
        const strategy = strategySelect.value;
        const response = await fetch(`${API_BASE}/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: currentTasks,
                strategy: strategy
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to analyze tasks');
        }
        
        const data = await response.json();
        displayAnalyzedTasks(data.tasks);
        
        if (data.warning) {
            showWarning(data.warning);
        }
        
    } catch (error) {
        showError('Error analyzing tasks: ' + error.message);
    } finally {
        showLoading(false);
    }
});

// Get suggestions
suggestBtn.addEventListener('click', async () => {
    if (currentTasks.length === 0) {
        showError('Please add at least one task');
        return;
    }
    
    showLoading(true);
    hideError();
    
    try {
        const strategy = strategySelect.value;
        const response = await fetch(`${API_BASE}/suggest/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: currentTasks,
                strategy: strategy
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to get suggestions');
        }
        
        const data = await response.json();
        displaySuggestions(data.suggestions);
        
    } catch (error) {
        showError('Error getting suggestions: ' + error.message);
    } finally {
        showLoading(false);
    }
});

// Clear all tasks
clearBtn.addEventListener('click', () => {
    if (currentTasks.length === 0) {
        return;
    }
    
    if (confirm('Are you sure you want to clear all tasks?')) {
        currentTasks = [];
        updateCurrentTasksList();
        resultsContainer.innerHTML = '<div class="empty-state"><p>👈 Add tasks and click "Analyze Tasks" to see prioritized results</p></div>';
        tasksContainer.classList.add('hidden');
        suggestionsContainer.classList.add('hidden');
        showSuccessMessage('All tasks cleared');
    }
});

// Display analyzed tasks
function displayAnalyzedTasks(tasks) {
    resultsContainer.innerHTML = '';
    tasksContainer.classList.remove('hidden');
    suggestionsContainer.classList.add('hidden');
    tasksList.innerHTML = '';
    
    tasks.forEach((task, index) => {
        const taskElement = createTaskElement(task, index + 1);
        tasksList.appendChild(taskElement);
    });
}

// Display suggestions
function displaySuggestions(suggestions) {
    suggestionsContainer.classList.remove('hidden');
    tasksContainer.classList.add('hidden');
    resultsContainer.innerHTML = '';
    suggestionsList.innerHTML = '';
    
    if (suggestions.length === 0) {
        suggestionsList.innerHTML = '<p class="empty-state">No suggestions available</p>';
        return;
    }
    
    suggestions.forEach((task, index) => {
        const taskElement = createTaskElement(task, index + 1, true);
        suggestionsList.appendChild(taskElement);
    });
}

// Create task element
function createTaskElement(task, rank, isSuggestion = false) {
    const div = document.createElement('div');
    div.className = `task-item priority-${task.priority_level.toLowerCase()}`;
    
    const priorityClass = task.priority_level.toLowerCase();
    
    div.innerHTML = `
        ${isSuggestion ? `<div style="font-size: 2em; font-weight: bold; color: #667eea; margin-bottom: 10px;">🏆 #${rank}</div>` : ''}
        <div class="task-header">
            <div class="task-title">${task.title}</div>
            <span class="priority-badge ${priorityClass}">${task.priority_level}</span>
        </div>
        
        <div class="task-score">Priority Score: ${task.priority_score.toFixed(2)}</div>
        
        <div class="task-details">
            <div class="task-detail-item">
                <span class="task-detail-label">Due Date</span>
                <span class="task-detail-value">${formatDate(task.due_date)}</span>
            </div>
            <div class="task-detail-item">
                <span class="task-detail-label">Estimated Hours</span>
                <span class="task-detail-value">${task.estimated_hours}h</span>
            </div>
            <div class="task-detail-item">
                <span class="task-detail-label">Importance</span>
                <span class="task-detail-value">${task.importance}/10</span>
            </div>
        </div>
        
        <div class="task-explanation">
            <strong>Why this priority?</strong> ${task.explanation}
        </div>
        
        ${task.breakdown ? `
            <div class="task-breakdown">
                <div class="breakdown-item">
                    <div class="breakdown-label">Urgency</div>
                    <div class="breakdown-value">${task.breakdown.urgency.toFixed(0)}</div>
                </div>
                <div class="breakdown-item">
                    <div class="breakdown-label">Importance</div>
                    <div class="breakdown-value">${task.breakdown.importance.toFixed(0)}</div>
                </div>
                <div class="breakdown-item">
                    <div class="breakdown-label">Effort</div>
                    <div class="breakdown-value">${task.breakdown.effort.toFixed(0)}</div>
                </div>
                <div class="breakdown-item">
                    <div class="breakdown-label">Dependencies</div>
                    <div class="breakdown-value">${task.breakdown.dependency_boost.toFixed(0)}</div>
                </div>
            </div>
        ` : ''}
    `;
    
    return div;
}

// Update current tasks list
function updateCurrentTasksList() {
    taskCount.textContent = currentTasks.length;
    
    if (currentTasks.length === 0) {
        currentTasksList.innerHTML = '<p class="empty-state">No tasks added yet</p>';
        return;
    }
    
    currentTasksList.innerHTML = '';
    currentTasks.forEach((task, index) => {
        const div = document.createElement('div');
        div.className = 'current-task-item';
        div.innerHTML = `
            <strong>${index + 1}. ${task.title}</strong> - 
            Due: ${formatDate(task.due_date)}, 
            Hours: ${task.estimated_hours}, 
            Importance: ${task.importance}/10
        `;
        currentTasksList.appendChild(div);
    });
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const taskDate = new Date(date);
    taskDate.setHours(0, 0, 0, 0);
    
    const diffTime = taskDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
        return `${date.toLocaleDateString()} (${Math.abs(diffDays)} days overdue!)`;
    } else if (diffDays === 0) {
        return `${date.toLocaleDateString()} (Today!)`;
    } else if (diffDays === 1) {
        return `${date.toLocaleDateString()} (Tomorrow)`;
    } else if (diffDays <= 7) {
        return `${date.toLocaleDateString()} (in ${diffDays} days)`;
    }
    
    return date.toLocaleDateString();
}

// Show/hide loading
function showLoading(show) {
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

// Show error
function showError(message) {
    errorMessage.textContent = '❌ ' + message;
    errorMessage.classList.remove('hidden');
    setTimeout(() => {
        errorMessage.classList.add('hidden');
    }, 5000);
}

// Hide error
function hideError() {
    errorMessage.classList.add('hidden');
}

// Show warning
function showWarning(message) {
    const warningDiv = document.createElement('div');
    warningDiv.className = 'error-message';
    warningDiv.style.background = '#fef3c7';
    warningDiv.style.color = '#92400e';
    warningDiv.style.borderLeftColor = '#f59e0b';
    warningDiv.textContent = '⚠️ ' + message;
    resultsContainer.insertBefore(warningDiv, resultsContainer.firstChild);
}

// Show success message
function showSuccessMessage(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = '✅ ' + message;
    successDiv.style.position = 'fixed';
    successDiv.style.top = '20px';
    successDiv.style.right = '20px';
    successDiv.style.zIndex = '1000';
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Sample data loader (for testing)
function loadSampleData() {
    const today = new Date();
    const sampleTasks = [
        {
            id: 1,
            title: "Fix critical login bug",
            due_date: today.toISOString().split('T')[0],
            estimated_hours: 2,
            importance: 10,
            dependencies: []
        },
        {
            id: 2,
            title: "Update documentation",
            due_date: new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            estimated_hours: 4,
            importance: 5,
            dependencies: [1]
        },
        {
            id: 3,
            title: "Code review for PR #234",
            due_date: new Date(today.getTime() + 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            estimated_hours: 1,
            importance: 7,
            dependencies: []
        },
        {
            id: 4,
            title: "Implement new feature",
            due_date: new Date(today.getTime() + 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            estimated_hours: 8,
            importance: 8,
            dependencies: [1, 2]
        },
        {
            id: 5,
            title: "Performance optimization",
            due_date: new Date(today.getTime() - 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            estimated_hours: 6,
            importance: 9,
            dependencies: []
        }
    ];
    
    currentTasks = sampleTasks;
    updateCurrentTasksList();
    showSuccessMessage('Sample data loaded!');
}

// Add keyboard shortcut to load sample data (Ctrl+Shift+S)
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'S') {
        loadSampleData();
    }
});