from tornado import gen
from tornado.escape import json_encode

from decorators import authenticated
from handlers.base import BaseHandler
from schemas import TaskSchema
from settings import TaskStatus


class TaskHandler(BaseHandler):
    @authenticated
    @gen.coroutine
    def get(self, task_id=None):
        user = self.get_current_user()
        c = self.db.cursor()
        if task_id:
            # Get one task
            c.execute(
                'SELECT * FROM tasks WHERE id = ? AND user_id = ?',
                (task_id, user['id'],)
            )
            task = c.fetchone()
            task = dict(zip(task.keys(), task)) if task else None
            task['status'] = TaskStatus(int(task['status'])).name
            self.write(json_encode(task))
        else:
            # List of user's tasks
            c.execute(
                'SELECT * FROM tasks WHERE user_id = ? ORDER BY created DESC',
                (user['id'], )
            )
            tasks = [dict(zip(t.keys(), t)) for t in c.fetchall()]
            for task in tasks:
                task['status'] = TaskStatus(int(task['status'])).name
            self.write(json_encode(tasks))
