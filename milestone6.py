# milestone6.py
import unittest
import json
import os
from milestone1 import Task, load_tasks, save_tasks, DATA_FILE

class TestTaskManager(unittest.TestCase):

    def setUp(self):
        self.test_tasks = [
            Task("Test1", "Description1", "high", "2025-04-20", ["work"], "Pending"),
            Task("Test2", "Description2", "low", "2025-04-25", ["home"], "Completed")
        ]
        save_tasks(self.test_tasks)

    def tearDown(self):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)

    def test_task_save_and_load(self):
        loaded_tasks = load_tasks()
        self.assertEqual(len(loaded_tasks), 2)
        self.assertEqual(loaded_tasks[0].title, "Test1")
        self.assertEqual(loaded_tasks[1].status, "Completed")

    def test_task_dict_conversion(self):
        task = self.test_tasks[0]
        task_dict = task.to_dict()
        new_task = Task.from_dict(task_dict)
        self.assertEqual(task.title, new_task.title)
        self.assertEqual(task.due_date, new_task.due_date)

if __name__ == '__main__':
    unittest.main()


