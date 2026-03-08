"""
Tests for ScheduleOptimizer
"""
from tulgatech.engine.schedule_optimizer import Task, ScheduleOptimizer
from datetime import datetime, timedelta


def test_task_init():
    """Test Task initialization"""
    task = Task("T001", "Foundation")
    assert task.id == "T001"
    assert task.name == "Foundation"
    assert task.duration_days == 1


def test_task_to_dict():
    """Test task to_dict"""
    task = Task("T001", "Foundation")
    task.duration_days = 5
    
    d = task.to_dict()
    assert d["id"] == "T001"
    assert d["duration_days"] == 5


def test_optimizer_init():
    """Test ScheduleOptimizer initialization"""
    opt = ScheduleOptimizer()
    assert opt.tasks == []
    assert opt.start_date is not None


def test_create_schedule():
    """Test creating schedule from analysis"""
    opt = ScheduleOptimizer()
    
    tasks = opt.create_schedule_from_analysis(
        walls_count=20,
        rooms_count=5,
        total_area_m2=100.0
    )
    
    assert len(tasks) == 5  # 5 main tasks
    assert opt.total_duration_days > 0


def test_schedule_dates():
    """Test schedule date calculations"""
    opt = ScheduleOptimizer()
    
    opt.create_schedule_from_analysis(10, 3, 50.0)
    
    assert opt.start_date < opt.end_date
    assert (opt.end_date - opt.start_date).days == opt.total_duration_days


def test_get_critical_path():
    """Test getting critical path"""
    opt = ScheduleOptimizer()
    
    opt.create_schedule_from_analysis(20, 5, 100.0)
    path = opt.get_critical_path()
    
    assert len(path) > 0
    assert path[0] == "T001"  # Should start with prep


def test_get_schedule_summary():
    """Test schedule summary"""
    opt = ScheduleOptimizer()
    
    opt.create_schedule_from_analysis(20, 5, 100.0)
    summary = opt.get_schedule_summary()
    
    assert "total_tasks" in summary
    assert "total_duration_days" in summary
    assert summary["total_tasks"] == 5


def test_optimize_parallel_tasks():
    """Test parallel task optimization"""
    opt = ScheduleOptimizer()
    
    opt.create_schedule_from_analysis(20, 5, 100.0)
    parallel = opt.optimize_parallel_tasks()
    
    assert "parallel_groups" in parallel
    assert "optimization_potential" in parallel


def test_estimate_labor():
    """Test labor requirement estimation"""
    opt = ScheduleOptimizer()
    
    opt.create_schedule_from_analysis(20, 5, 100.0)
    labor = opt.estimate_labor_requirement()
    
    assert "total_worker_days" in labor
    assert "average_workers_needed" in labor
    assert labor["average_workers_needed"] > 0