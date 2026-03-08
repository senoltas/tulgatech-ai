"""
Project schedule optimization
"""
from typing import List, Dict, Tuple
from datetime import datetime, timedelta


class Task:
    """Represents a construction task"""
    def __init__(self, task_id: str, task_name: str):
        self.id = task_id
        self.name = task_name
        self.duration_days = 1
        self.start_date = None
        self.end_date = None
        self.dependencies: List[str] = []
        self.resource_count = 1
        self.priority = "normal"  # low, normal, high
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "duration_days": self.duration_days,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "dependencies": self.dependencies,
            "resource_count": self.resource_count,
            "priority": self.priority
        }


class ScheduleOptimizer:
    """Optimize project schedule"""
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.start_date = datetime.now()
        self.end_date = None
        self.total_duration_days = 0
    
    def create_schedule_from_analysis(self, walls_count: int,
                                     rooms_count: int,
                                     total_area_m2: float) -> List[Task]:
        """Create project schedule from analysis data"""
        
        self.tasks = []
        current_date = self.start_date
        
        # Task 1: Preparation & Planning (3-5 days)
        prep_days = 5
        task_prep = Task("T001", "Site Preparation & Planning")
        task_prep.duration_days = prep_days
        task_prep.start_date = current_date
        task_prep.end_date = current_date + timedelta(days=prep_days)
        task_prep.priority = "high"
        self.tasks.append(task_prep)
        current_date = task_prep.end_date
        
        # Task 2: Wall Construction (based on wall count)
        wall_days = max(5, walls_count // 4)  # 4 walls per day
        task_walls = Task("T002", "Wall Construction")
        task_walls.duration_days = wall_days
        task_walls.start_date = current_date
        task_walls.end_date = current_date + timedelta(days=wall_days)
        task_walls.dependencies = ["T001"]
        task_walls.priority = "high"
        self.tasks.append(task_walls)
        current_date = task_walls.end_date
        
        # Task 3: Flooring (based on room count & area)
        flooring_days = max(3, int(total_area_m2 / 50))  # 50 m2 per day
        task_flooring = Task("T003", "Flooring Installation")
        task_flooring.duration_days = flooring_days
        task_flooring.start_date = current_date
        task_flooring.end_date = current_date + timedelta(days=flooring_days)
        task_flooring.dependencies = ["T002"]
        self.tasks.append(task_flooring)
        current_date = task_flooring.end_date
        
        # Task 4: Painting (based on wall area)
        paint_days = max(3, walls_count // 2)
        task_paint = Task("T004", "Painting & Finishing")
        task_paint.duration_days = paint_days
        task_paint.start_date = current_date
        task_paint.end_date = current_date + timedelta(days=paint_days)
        task_paint.dependencies = ["T003"]
        self.tasks.append(task_paint)
        current_date = task_paint.end_date
        
        # Task 5: Final Inspection (2 days)
        task_inspection = Task("T005", "Final Inspection & QA")
        task_inspection.duration_days = 2
        task_inspection.start_date = current_date
        task_inspection.end_date = current_date + timedelta(days=2)
        task_inspection.dependencies = ["T004"]
        self.tasks.append(task_inspection)
        
        self.end_date = task_inspection.end_date
        self.total_duration_days = (self.end_date - self.start_date).days
        
        return self.tasks
    
    def get_critical_path(self) -> List[str]:
        """Get critical path (longest dependency chain)"""
        if not self.tasks:
            return []
        
        # Find task with no dependencies (start task)
        start_tasks = [t for t in self.tasks if not t.dependencies]
        
        if not start_tasks:
            return []
        
        # Build path from start to end
        path = [start_tasks[0].id]
        current_task = start_tasks[0]
        
        while current_task:
            # Find tasks that depend on current
            dependent_tasks = [t for t in self.tasks 
                             if current_task.id in t.dependencies]
            
            if dependent_tasks:
                # Take the longest dependent task
                current_task = max(dependent_tasks, 
                                 key=lambda t: t.duration_days)
                path.append(current_task.id)
            else:
                current_task = None
        
        return path
    
    def get_schedule_summary(self) -> Dict:
        """Get schedule summary"""
        return {
            "total_tasks": len(self.tasks),
            "total_duration_days": self.total_duration_days,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "critical_path": self.get_critical_path(),
            "tasks": [t.to_dict() for t in self.tasks]
        }
    
    def optimize_parallel_tasks(self) -> Dict:
        """Identify tasks that can run in parallel"""
        parallel_groups = {}
        
        for task in self.tasks:
            if not task.dependencies:
                key = "independent"
            else:
                key = str(task.dependencies)
            
            if key not in parallel_groups:
                parallel_groups[key] = []
            
            parallel_groups[key].append(task.id)
        
        return {
            "parallel_groups": parallel_groups,
            "optimization_potential": len([g for g in parallel_groups.values() if len(g) > 1])
        }
    
    def estimate_labor_requirement(self) -> Dict:
        """Estimate labor requirements"""
        total_worker_days = sum(t.duration_days * t.resource_count 
                               for t in self.tasks)
        avg_workers = total_worker_days / self.total_duration_days if self.total_duration_days > 0 else 0
        
        return {
            "total_worker_days": total_worker_days,
            "average_workers_needed": round(avg_workers, 1),
            "total_duration_days": self.total_duration_days,
            "tasks_breakdown": {
                t.id: {
                    "name": t.name,
                    "worker_days": t.duration_days * t.resource_count
                }
                for t in self.tasks
            }
        }