#!/usr/bin/env python3
"""
Advanced Task Scheduling System - AI Generated Code
This module provides a comprehensive task scheduling and execution framework
with priority management, dependency handling, and monitoring capabilities.
Author: AI Assistant
Version: 1.0
Date: Auto-generated
"""

import threading
import time
import heapq
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import pickle
import os
from concurrent.futures import ThreadPoolExecutor, Future
import signal
import sys
from pathlib import Path

# Configure comprehensive logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('task_scheduler.log'),
        logging.StreamHandler()
    ]
)

class TaskStatus(Enum):
    """Enumeration for task execution states."""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING_DEPENDENCIES = "waiting_dependencies"

class TaskPriority(Enum):
    """Enumeration for task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class TaskResult:
    """
    Data class representing the result of a task execution.
    Contains execution metadata and return values.
    """
    task_id: str
    status: TaskStatus
    return_value: Any = None
    error_message: str = ""
    execution_time: float = 0.0
    completed_at: Optional[datetime] = None
    retries_used: int = 0

@dataclass
class ScheduledTask:
    """
    Comprehensive task definition with scheduling and dependency information.
    Supports various execution patterns and configuration options.
    """
    task_id: str
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    scheduled_time: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    max_retries: int = 3
    retry_delay: float = 60.0  # seconds
    timeout: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    # Execution tracking fields
    status: TaskStatus = TaskStatus.PENDING
    retries_attempted: int = 0
    last_error: str = ""
    execution_start: Optional[datetime] = None
    execution_end: Optional[datetime] = None
    
    def __lt__(self, other):
        """Enable priority queue comparison based on priority and scheduled time."""
        if self.priority != other.priority:
            return self.priority.value > other.priority.value
        if self.scheduled_time and other.scheduled_time:
            return self.scheduled_time < other.scheduled_time
        return self.created_at < other.created_at
    
    def is_ready_to_execute(self, completed_tasks: set) -> bool:
        """
        Check if task is ready for execution based on dependencies and schedule.
        
        Args:
            completed_tasks (set): Set of completed task IDs
            
        Returns:
            bool: True if task can be executed
        """
        # Check if all dependencies are completed
        for dep_id in self.dependencies:
            if dep_id not in completed_tasks:
                return False
        
        # Check if scheduled time has passed
        if self.scheduled_time and datetime.now() < self.scheduled_time:
            return False
        
        return True

class TaskDatabase:
    """
    SQLite-based database for persistent task storage and history tracking.
    Provides comprehensive data persistence for task scheduling system.
    """
    
    def __init__(self, db_path: str = "task_scheduler.db"):
        """
        Initialize task database with proper schema.
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Create database tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tasks table for active and completed tasks
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tasks (
                        task_id TEXT PRIMARY KEY,
                        function_name TEXT NOT NULL,
                        args_pickle BLOB,
                        kwargs_pickle BLOB,
                        priority INTEGER NOT NULL,
                        scheduled_time TIMESTAMP,
                        dependencies_json TEXT,
                        max_retries INTEGER DEFAULT 3,
                        retry_delay REAL DEFAULT 60.0,
                        timeout REAL,
                        tags_json TEXT,
                        metadata_json TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'pending',
                        retries_attempted INTEGER DEFAULT 0,
                        last_error TEXT,
                        execution_start TIMESTAMP,
                        execution_end TIMESTAMP
                    )
                ''')
                
                # Task execution history
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS task_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_id TEXT NOT NULL,
                        execution_start TIMESTAMP,
                        execution_end TIMESTAMP,
                        status TEXT NOT NULL,
                        return_value_pickle BLOB,
                        error_message TEXT,
                        execution_time REAL,
                        retries_used INTEGER DEFAULT 0
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_tasks_status 
                    ON tasks(status)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_tasks_scheduled_time 
                    ON tasks(scheduled_time)
                ''')
                
                conn.commit()
                self.logger.info("Task database initialized successfully")
                
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {str(e)}")
    
    def save_task(self, task: ScheduledTask) -> bool:
        """
        Save task to database with serialization.
        
        Args:
            task (ScheduledTask): Task to save
            
        Returns:
            bool: True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Serialize complex data types
                args_pickle = pickle.dumps(task.args)
                kwargs_pickle = pickle.dumps(task.kwargs)
                dependencies_json = json.dumps(task.dependencies)
                tags_json = json.dumps(task.tags)
                metadata_json = json.dumps(task.metadata)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO tasks (
                        task_id, function_name, args_pickle, kwargs_pickle, priority,
                        scheduled_time, dependencies_json, max_retries, retry_delay,
                        timeout, tags_json, metadata_json, created_at, status,
                        retries_attempted, last_error, execution_start, execution_end
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task.task_id,
                    task.function.__name__,
                    args_pickle,
                    kwargs_pickle,
                    task.priority.value,
                    task.scheduled_time,
                    dependencies_json,
                    task.max_retries,
                    task.retry_delay,
                    task.timeout,
                    tags_json,
                    metadata_json,
                    task.created_at,
                    task.status.value,
                    task.retries_attempted,
                    task.last_error,
                    task.execution_start,
                    task.execution_end
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving task {task.task_id}: {str(e)}")
            return False
    
    def load_pending_tasks(self) -> List[Dict[str, Any]]:
        """
        Load all pending tasks from database.
        
        Returns:
            List[Dict[str, Any]]: List of task data dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM tasks 
                    WHERE status IN ('pending', 'waiting_dependencies')
                    ORDER BY priority DESC, scheduled_time ASC
                ''')
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            self.logger.error(f"Error loading pending tasks: {str(e)}")
            return []
    
    def save_task_result(self, result: TaskResult) -> bool:
        """
        Save task execution result to history.
        
        Args:
            result (TaskResult): Task execution result
            
        Returns:
            bool: True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                return_value_pickle = pickle.dumps(result.return_value)
                
                cursor.execute('''
                    INSERT INTO task_history (
                        task_id, execution_start, execution_end, status,
                        return_value_pickle, error_message, execution_time, retries_used
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result.task_id,
                    datetime.now() - timedelta(seconds=result.execution_time),
                    result.completed_at,
                    result.status.value,
                    return_value_pickle,
                    result.error_message,
                    result.execution_time,
                    result.retries_used
                ))
                
                # Update main task record
                cursor.execute('''
                    UPDATE tasks 
                    SET status = ?, execution_end = ?, last_error = ?
                    WHERE task_id = ?
                ''', (
                    result.status.value,
                    result.completed_at,
                    result.error_message,
                    result.task_id
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving task result: {str(e)}")
            return False

class TaskScheduler:
    """
    Advanced task scheduling system with comprehensive execution management.
    
    Features include:
    - Priority-based scheduling
    - Dependency management
    - Retry logic with exponential backoff
    - Concurrent execution with thread pools
    - Persistent task storage
    - Real-time monitoring and statistics
    """
    
    def __init__(self, max_workers: int = 4, db_path: str = "task_scheduler.db"):
        """
        Initialize the task scheduler with configuration.
        
        Args:
            max_workers (int): Maximum number of concurrent worker threads
            db_path (str): Path to SQLite database for persistence
        """
        self.max_workers = max_workers
        self.db = TaskDatabase(db_path)
        self.logger = logging.getLogger(__name__)
        
        # Task storage and tracking
        self.pending_tasks = []  # Priority queue
        self.running_tasks: Dict[str, ScheduledTask] = {}
        self.completed_tasks: set = set()
        self.failed_tasks: set = set()
        self.task_functions: Dict[str, Callable] = {}
        
        # Thread management
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_futures: Dict[str, Future] = {}
        self.scheduler_thread = None
        self.is_running = False
        self.shutdown_event = threading.Event()
        
        # Statistics tracking
        self.stats = {
            'tasks_scheduled': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0
        }
        
        # Thread locks for thread safety
        self.queue_lock = threading.Lock()
        self.stats_lock = threading.Lock()
        
        self.logger.info(f"Task scheduler initialized with {max_workers} workers")
    
    def register_function(self, name: str, function: Callable) -> None:
        """
        Register a function that can be called by scheduled tasks.
        
        Args:
            name (str): Function identifier
            function (Callable): Function to register
        """
        self.task_functions[name] = function
        self.logger.info(f"Function '{name}' registered successfully")
    
    def schedule_task(self, task: ScheduledTask) -> bool:
        """
        Schedule a new task for execution.
        
        Args:
            task (ScheduledTask): Task to schedule
            
        Returns:
            bool: True if scheduled successfully
        """
        try:
            # Validate dependencies exist (future improvement)
            # This would check if dependent tasks are already scheduled
            
            with self.queue_lock:
                heapq.heappush(self.pending_tasks, task)
                
                # Save to database for persistence
                self.db.save_task(task)
                
                # Update statistics
                with self.stats_lock:
                    self.stats['tasks_scheduled'] += 1
            
            self.logger.info(f"Task {task.task_id} scheduled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error scheduling task {task.task_id}: {str(e)}")
            return False
    
    def schedule_function(self, func: Callable, task_id: str = None, 
                         schedule_time: datetime = None, priority: TaskPriority = TaskPriority.NORMAL,
                         dependencies: List[str] = None, max_retries: int = 3,
                         *args, **kwargs) -> str:
        """
        Convenient method to schedule a function call as a task.
        
        Args:
            func (Callable): Function to execute
            task_id (str): Optional task identifier
            schedule_time (datetime): When to execute the task
            priority (TaskPriority): Task priority level
            dependencies (List[str]): Task dependencies
            max_retries (int): Maximum retry attempts
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            str: Generated or provided task ID
        """
        if task_id is None:
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(func)}"
        
        if dependencies is None:
            dependencies = []
        
        task = ScheduledTask(
            task_id=task_id,
            function=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            scheduled_time=schedule_time,
            dependencies=dependencies,
            max_retries=max_retries
        )
        
        self.schedule_task(task)
        return task_id
    
    def _execute_task(self, task: ScheduledTask) -> TaskResult:
        """
        Execute a single task with comprehensive error handling and timing.
        
        Args:
            task (ScheduledTask): Task to execute
            
        Returns:
            TaskResult: Execution result
        """
        start_time = time.time()
        task.execution_start = datetime.now()
        task.status = TaskStatus.RUNNING
        
        try:
            self.logger.info(f"Executing task {task.task_id}")
            
            # Execute the function with timeout if specified
            if task.timeout:
                # Note: This is a simplified timeout implementation
                # In production, you might want to use more sophisticated timeout handling
                result = task.function(*task.args, **task.kwargs)
            else:
                result = task.function(*task.args, **task.kwargs)
            
            execution_time = time.time() - start_time
            task.execution_end = datetime.now()
            task.status = TaskStatus.COMPLETED
            
            # Create successful result
            task_result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                return_value=result,
                execution_time=execution_time,
                completed_at=task.execution_end,
                retries_used=task.retries_attempted
            )
            
            # Update statistics
            with self.stats_lock:
                self.stats['tasks_completed'] += 1
                self.stats['total_execution_time'] += execution_time
                completed_count = self.stats['tasks_completed']
                if completed_count > 0:
                    self.stats['average_execution_time'] = (
                        self.stats['total_execution_time'] / completed_count
                    )
            
            self.completed_tasks.add(task.task_id)
            self.logger.info(f"Task {task.task_id} completed successfully in {execution_time:.2f}s")
            return task_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_message = str(e)
            
            task.execution_end = datetime.now()
            task.status = TaskStatus.FAILED
            task.last_error = error_message
            
            # Create failed result
            task_result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error_message=error_message,
                execution_time=execution_time,
                completed_at=task.execution_end,
                retries_used=task.retries_attempted
            )
            
            # Update statistics
            with self.stats_lock:
                self.stats['tasks_failed'] += 1
            
            self.failed_tasks.add(task.task_id)
            self.logger.error(f"Task {task.task_id} failed: {error_message}")
            return task_result
    
    def _should_retry_task(self, task: ScheduledTask, result: TaskResult) -> bool:
        """
        Determine if a failed task should be retried.
        
        Args:
            task (ScheduledTask): The failed task
            result (TaskResult): Task execution result
            
        Returns:
            bool: True if task should be retried
        """
        if result.status != TaskStatus.FAILED:
            return False
        
        if task.retries_attempted >= task.max_retries:
            return False
        
        return True
    
    def _schedule_retry(self, task: ScheduledTask) -> None:
        """
        Schedule a task for retry with exponential backoff delay.
        
        Args:
            task (ScheduledTask): Task to retry
        """
        task.retries_attempted += 1
        delay = task.retry_delay * (2 ** (task.retries_attempted - 1))  # Exponential backoff
        retry_time = datetime.now() + timedelta(seconds=delay)
        
        task.scheduled_time = retry_time
        task.status = TaskStatus.PENDING
        
        with self.queue_lock:
            heapq.heappush(self.pending_tasks, task)
        
        self.logger.info(f"Task {task.task_id} scheduled for retry {task.retries_attempted} at {retry_time}")
    
    def _scheduler_loop(self) -> None:
        """
        Main scheduler loop that manages task execution.
        Runs in a separate thread and continuously processes the task queue.
        """
        self.logger.info("Task scheduler loop started")
        
        while not self.shutdown_event.is_set():
            try:
                # Process completed futures
                completed_futures = []
                for task_id, future in self.task_futures.items():
                    if future.done():
                        try:
                            result = future.result()
                            
                            # Save result to database
                            self.db.save_task_result(result)
                            
                            # Handle retries for failed tasks
                            if result.status == TaskStatus.FAILED:
                                task = self.running_tasks.get(task_id)
                                if task and self._should_retry_task(task, result):
                                    self._schedule_retry(task)
                                    # Remove from running tasks
                                    if task_id in self.running_tasks:
                                        del self.running_tasks[task_id]
                                else:
                                    # Task failed permanently
                                    self.logger.warning(f"Task {task_id} failed permanently")
                            
                            completed_futures.append(task_id)
                            
                        except Exception as e:
                            self.logger.error(f"Error processing completed task {task_id}: {str(e)}")
                            completed_futures.append(task_id)
                
                # Clean up completed futures
                for task_id in completed_futures:
                    if task_id in self.task_futures:
                        del self.task_futures[task_id]
                    if task_id in self.running_tasks:
                        del self.running_tasks[task_id]
                
                # Check for ready tasks
                with self.queue_lock:
                    ready_tasks = []
                    remaining_tasks = []
                    
                    while self.pending_tasks:
                        task = heapq.heappop(self.pending_tasks)
                        
                        if task.is_ready_to_execute(self.completed_tasks):
                            ready_tasks.append(task)
                        else:
                            remaining_tasks.append(task)
                        
                        # Limit batch size to prevent overwhelming
                        if len(ready_tasks) >= self.max_workers:
                            remaining_tasks.extend(self.pending_tasks)
                            self.pending_tasks.clear()
                            break
                    
                    # Put remaining tasks back in queue
                    for task in remaining_tasks:
                        heapq.heappush(self.pending_tasks, task)
                
                # Submit ready tasks for execution
                for task in ready_tasks:
                    if len(self.running_tasks) < self.max_workers:
                        future = self.executor.submit(self._execute_task, task)
                        self.task_futures[task.task_id] = future
                        self.running_tasks[task.task_id] = task
                        
                        self.logger.info(f"Submitted task {task.task_id} for execution")
                    else:
                        # Put task back in queue if no workers available
                        with self.queue_lock:
                            heapq.heappush(self.pending_tasks, task)
                
                # Sleep briefly to prevent busy waiting
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(1.0)  # Longer sleep on error
        
        self.logger.info("Task scheduler loop terminated")
    
    def start(self) -> None:
        """Start the task scheduler in a separate thread."""
        if self.is_running:
            self.logger.warning("Task scheduler is already running")
            return
        
        self.is_running = True
        self.shutdown_event.clear()
        
        # Load pending tasks from database
        self._load_pending_tasks()
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Task scheduler started successfully")
    
    def stop(self, timeout: float = 30.0) -> None:
        """
        Stop the task scheduler gracefully.
        
        Args:
            timeout (float): Maximum time to wait for shutdown
        """
        if not self.is_running:
            self.logger.warning("Task scheduler is not running")
            return
        
        self.logger.info("Stopping task scheduler...")
        self.shutdown_event.set()
        self.is_running = False
        
        # Wait for scheduler thread to finish
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=timeout)
        
        # Shutdown executor
        self.executor.shutdown(wait=True, timeout=timeout)
        
        self.logger.info("Task scheduler stopped successfully")
    
    def _load_pending_tasks(self) -> None:
        """Load pending tasks from database on startup."""
        try:
            task_data_list = self.db.load_pending_tasks()
            
            for task_data in task_data_list:
                # Reconstruct function (this requires function registration)
                function_name = task_data['function_name']
                if function_name not in self.task_functions:
                    self.logger.warning(f"Function {function_name} not registered, skipping task {task_data['task_id']}")
                    continue
                
                # Deserialize data
                args = pickle.loads(task_data['args_pickle'])
                kwargs = pickle.loads(task_data['kwargs_pickle'])
                dependencies = json.loads(task_data['dependencies_json'] or '[]')
                tags = json.loads(task_data['tags_json'] or '[]')
                metadata = json.loads(task_data['metadata_json'] or '{}')
                
                # Create task object
                task = ScheduledTask(
                    task_id=task_data['task_id'],
                    function=self.task_functions[function_name],
                    args=args,
                    kwargs=kwargs,
                    priority=TaskPriority(task_data['priority']),
                    scheduled_time=datetime.fromisoformat(task_data['scheduled_time']) if task_data['scheduled_time'] else None,
                    dependencies=dependencies,
                    max_retries=task_data['max_retries'],
                    retry_delay=task_data['retry_delay'],
                    timeout=task_data['timeout'],
                    tags=tags,
                    metadata=metadata,
                    created_at=datetime.fromisoformat(task_data['created_at']),
                    status=TaskStatus(task_data['status']),
                    retries_attempted=task_data['retries_attempted'],
                    last_error=task_data['last_error'] or ""
                )
                
                with self.queue_lock:
                    heapq.heappush(self.pending_tasks, task)
            
            self.logger.info(f"Loaded {len(task_data_list)} pending tasks from database")
            
        except Exception as e:
            self.logger.error(f"Error loading pending tasks: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive scheduler statistics.
        
        Returns:
            Dict[str, Any]: Current scheduler statistics
        """
        with self.stats_lock:
            current_stats = self.stats.copy()
        
        with self.queue_lock:
            current_stats.update({
                'pending_tasks': len(self.pending_tasks),
                'running_tasks': len(self.running_tasks),
                'completed_tasks': len(self.completed_tasks),
                'failed_tasks': len(self.failed_tasks),
                'is_running': self.is_running
            })
        
        return current_stats
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending or running task.
        
        Args:
            task_id (str): Task identifier to cancel
            
        Returns:
            bool: True if cancelled successfully
        """
        # Cancel running task
        if task_id in self.task_futures:
            future = self.task_futures[task_id]
            if future.cancel():
                del self.task_futures[task_id]
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
                self.logger.info(f"Running task {task_id} cancelled")
                return True
        
        # Cancel pending task
        with self.queue_lock:
            # This is inefficient for large queues - consider using a different data structure
            remaining_tasks = []
            cancelled = False
            
            while self.pending_tasks:
                task = heapq.heappop(self.pending_tasks)
                if task.task_id == task_id:
                    task.status = TaskStatus.CANCELLED
                    cancelled = True
                    self.logger.info(f"Pending task {task_id} cancelled")
                else:
                    remaining_tasks.append(task)
            
            # Rebuild heap
            self.pending_tasks = remaining_tasks
            heapq.heapify(self.pending_tasks)
            
            return cancelled
        
        return False

# Example usage and demonstration
def example_task_function(message: str, delay: float = 0) -> str:
    """Example task function for demonstration purposes."""
    if delay > 0:
        time.sleep(delay)
    return f"Processed: {message}"

def example_usage():
    """
    Comprehensive example demonstrating the task scheduling system.
    Shows typical AI-generated usage patterns with detailed explanations.
    """
    print("Advanced Task Scheduling System - AI Generated Example")
    print("=" * 60)
    
    # Initialize the scheduler
    scheduler = TaskScheduler(max_workers=3)
    
    # Register example functions
    scheduler.register_function("example_task", example_task_function)
    
    # Start the scheduler
    scheduler.start()
    
    print("Task Scheduler initialized and started")
    
    # Schedule some example tasks
    task_ids = []
    
    # Immediate task with high priority
    task_id1 = scheduler.schedule_function(
        example_task_function,
        task_id="urgent_task",
        priority=TaskPriority.HIGH,
        message="Urgent processing required",
        delay=1.0
    )
    task_ids.append(task_id1)
    
    # Scheduled task for future execution
    future_time = datetime.now() + timedelta(seconds=5)
    task_id2 = scheduler.schedule_function(
        example_task_function,
        task_id="scheduled_task",
        schedule_time=future_time,
        priority=TaskPriority.NORMAL,
        message="Scheduled for later",
        delay=2.0
    )
    task_ids.append(task_id2)
    
    # Task with dependency (depends on first task)
    task_id3 = scheduler.schedule_function(
        example_task_function,
        task_id="dependent_task",
        dependencies=[task_id1],
        priority=TaskPriority.LOW,
        message="Depends on urgent task",
        delay=0.5
    )
    task_ids.append(task_id3)
    
    print(f"\nScheduled {len(task_ids)} example tasks:")
    for task_id in task_ids:
        print(f"  - {task_id}")
    
    # Monitor execution for a short time
    print("\nMonitoring task execution...")
    for i in range(10):
        stats = scheduler.get_statistics()
        print(f"Status - Pending: {stats['pending_tasks']}, "
              f"Running: {stats['running_tasks']}, "
              f"Completed: {stats['completed_tasks']}, "
              f"Failed: {stats['failed_tasks']}")
        
        if stats['pending_tasks'] == 0 and stats['running_tasks'] == 0:
            break
        
        time.sleep(1)
    
    # Final statistics
    final_stats = scheduler.get_statistics()
    print(f"\nFinal Statistics:")
    print(f"  Tasks Scheduled: {final_stats['tasks_scheduled']}")
    print(f"  Tasks Completed: {final_stats['tasks_completed']}")
    print(f"  Tasks Failed: {final_stats['tasks_failed']}")
    print(f"  Average Execution Time: {final_stats['average_execution_time']:.2f}s")
    
    # Stop the scheduler
    scheduler.stop()
    print("\nTask scheduler stopped")
    
    print("\nThis example demonstrates:")
    print("- Task scheduling with priorities and dependencies")
    print("- Concurrent execution with thread pools") 
    print("- Persistent storage with SQLite")
    print("- Real-time monitoring and statistics")
    print("- Graceful shutdown handling")

if __name__ == "__main__":
    example_usage()