# Smart Task Analyzer

A Django-based task management system that intelligently scores and prioritizes tasks based on multiple factors including urgency, importance, effort, and dependencies.

## 🎯 Project Overview

This application helps users identify which tasks they should work on first by analyzing tasks through a sophisticated priority scoring algorithm. It provides multiple sorting strategies and visual feedback to make task prioritization effortless.

---

## 📁 Project Structure

```
task-analyzer/
├── backend/
│   ├── manage.py
│   ├── task_analyzer/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── tasks/
│       ├── __init__.py
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       ├── scoring.py
│       ├── urls.py
│       ├── tests.py
│       └── admin.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── requirements.txt
└── README.md
```

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Step 1: Clone the Repository

```bash
# If you have a repository
git clone https://github.com/shubhamthakur-2504/task-analyzer.git
cd task-analyzer
```
### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Start the Development Server

```bash
python manage.py runserver
```

The server will start at `http://localhost:8000/`

## 🧠 Algorithm Explanation

### Priority Scoring Algorithm

The Smart Task Analyzer uses a sophisticated multi-factor algorithm to calculate priority scores for tasks. The algorithm considers four main components:

#### 1. **Urgency Score (0-150)**

Calculates how soon a task is due:
- **Overdue tasks**: 100 + (days overdue × 5), capped at 150
- **Due today**: 95
- **Due tomorrow**: 90
- **Due in 2-3 days**: 75
- **Due in 4-7 days**: 50
- **Due in 8-14 days**: 30
- **Due in 15+ days**: 10

**Rationale**: Overdue tasks receive penalty points to ensure they surface at the top. The scoring degrades exponentially as due dates move further out.

#### 2. **Importance Score (0-100)**

User-provided importance rating (1-10) converted to 0-100 scale:
- Simply multiply the user's rating by 10
- Allows users to manually boost critical tasks

**Rationale**: Gives users direct control over task priority when they know something is critical.

#### 3. **Effort Score (0-100)**

Inverse relationship with estimated hours:
- Formula: `100 / (estimated_hours + 0.5)`
- Lower effort tasks score higher
- Encourages "quick wins"

**Rationale**: Quick wins build momentum and clear mental bandwidth. The +0.5 prevents extreme values for very small tasks.

#### 4. **Dependency Boost (0-50)**

Additional points based on how many tasks depend on this one:
- Each dependent task adds 15 points
- Capped at 50 points maximum

**Rationale**: Tasks that block others should be completed first to unblock the team.

### Scoring Strategies

The algorithm supports four strategies with different weight distributions:

#### **Smart Balance** (Recommended)
```
Final Score = (Urgency × 0.35) + (Importance × 0.30) + 
              (Effort × 0.20) + (Dependency Boost × 1.0)
```
Balanced approach considering all factors equally.

#### **Fastest Wins**
```
Final Score = (Urgency × 0.20) + (Importance × 0.10) + 
              (Effort × 0.60) + (Dependency Boost × 0.5)
```
Heavily weights effort to surface quick wins.

#### **High Impact**
```
Final Score = (Urgency × 0.20) + (Importance × 0.60) + 
              (Effort × 0.10) + (Dependency Boost × 0.5)
```
Prioritizes user-defined important tasks.

#### **Deadline Driven**
```
Final Score = (Urgency × 0.60) + (Importance × 0.25) + 
              (Effort × 0.10) + (Dependency Boost × 0.3)
```
Focuses primarily on due dates.

### Edge Case Handling

1. **Missing Data**: Tasks with invalid data receive a score of 0 and marked as "Low" priority
2. **Very Low Effort**: +0.5 added to denominator prevents division issues
3. **Extreme Overdue**: Capped at 150 to prevent overflow

---

## 🎨 Design Decisions

### Backend Architecture

**1. Separation of Concerns**
- `models.py`: Data structure only
- `scoring.py`: Pure algorithm logic (no Django dependencies)
- `views.py`: API endpoints and request handling
- `serializers.py`: Data validation and transformation

**Rationale**: Makes the scoring algorithm testable independently and reusable in other contexts.

**2. Strategy Pattern**
- Different scoring strategies implemented as configuration
- Easy to add new strategies without changing core logic

**Rationale**: Provides flexibility for different user preferences and use cases.

**3. Stateless API**
- No session management required
- Tasks can be analyzed without persisting to database

**Rationale**: Simplifies usage and allows for easy testing.

### Frontend Architecture

**1. Vanilla JavaScript**
- No framework dependencies
- Direct DOM manipulation
- Simple fetch API calls

**Rationale**: Keeps bundle size small and performance high for a simple application.

**2. Responsive Design**
- CSS Grid for layout
- Mobile-first approach
- Breakpoints at 768px and 1024px

**Rationale**: Ensures usability across all device sizes.

**3. Real-time Feedback**
- Loading states during API calls
- Error messages with auto-dismiss
- Success notifications

**Rationale**: Improves user experience and reduces confusion.

### Trade-offs Made

**1. Client-side State vs Database**
- **Chosen**: Client-side state (tasks array in JavaScript)
- **Trade-off**: Tasks don't persist on refresh
- **Rationale**: Simplifies backend, meets assignment requirements, appropriate for demo

**2. Synchronous vs Asynchronous Analysis**
- **Chosen**: Synchronous API calls
- **Trade-off**: Might be slow for large task lists (100+ tasks)
- **Rationale**: Simpler implementation

---


## 🚀 Future Improvements

Given more time, I would implement:

### 1. **Persistence Layer** 
- Store tasks in database
- User authentication
- Task history and analytics

### 2. **Dependency Graph Visualization** 
- D3.js or vis.js for graph rendering
- Interactive circular dependency highlighting
- Visual task flow

### 3. **Advanced Date Intelligence** 
- Weekend/holiday awareness
- Business days calculation
- Timezone support

### 4. **Collaboration Features** 
- Share task lists with team
- Assign tasks to users
- Real-time updates with WebSockets

### 5. **Performance Optimization** 
- Caching frequently accessed scores
- Batch processing for large task lists
- Database indexing

### 6. **Enhanced UI/UX** 
- Drag-and-drop task reordering
- Filtering and search
- Dark mode
- Keyboard shortcuts

---

## 📡 API Endpoints

### POST `/api/tasks/analyze/`

Analyze and sort tasks by priority.

**Request:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Fix bug",
      "due_date": "2025-12-01",
      "estimated_hours": 2,
      "importance": 8,
      "dependencies": []
    }
  ],
  "strategy": "smart_balance"
}
```

**Response:**
```json
{
  "tasks": [...],
  "strategy_used": "smart_balance",
  "total_tasks": 1
}
```

### POST `/api/tasks/suggest/`

Get top 3 task suggestions.

**Request:**
```json
{
  "tasks": [...],
  "strategy": "smart_balance"
}
```

**Response:**
```json
{
  "suggestions": [...],
  "strategy_used": "smart_balance",
  "suggestion_count": 3
}
```

---

## 🧪 Running Tests

```bash
# Run all tests
python manage.py test tasks

# Run specific test
python manage.py test tasks.tests.TaskScorerTests.test_urgency_score_overdue_task

# Run with verbosity
python manage.py test tasks --verbosity=2
```

**Test Coverage:**
- Urgency score calculations
- Importance conversion
- Effort scoring
- Circular dependency detection
- Task sorting
- Different strategies
- Edge cases and invalid data
---

## 📝 Sample Data

Press `Ctrl + Shift + S` in the frontend to load sample data for testing.

Or use this JSON:

```json
[
  {
    "id": 1,
    "title": "Fix critical login bug",
    "due_date": "2025-11-30",
    "estimated_hours": 2,
    "importance": 10,
    "dependencies": []
  },
  {
    "id": 2,
    "title": "Update documentation",
    "due_date": "2025-12-07",
    "estimated_hours": 4,
    "importance": 5,
    "dependencies": [1]
  },
  {
    "id": 3,
    "title": "Code review PR #234",
    "due_date": "2025-12-01",
    "estimated_hours": 1,
    "importance": 7,
    "dependencies": []
  }
]
```

---

## 👨‍💻 Author
[**Shubham Thakur**](https://github.com/shubhamthakur-2504)
