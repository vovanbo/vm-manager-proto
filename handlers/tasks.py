from marshmallow.utils import isoformat
from tornado import gen
from tornado.escape import json_encode, json_decode

from decorators import authenticated
from handlers.base import BaseHandler
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
        else:
            # List of user's tasks
            c.execute(
                'SELECT * FROM tasks WHERE user_id = ? ORDER BY created DESC',
                (user['id'], )
            )

        tasks = [dict(zip(t.keys(), t)) for t in c.fetchall()]

        if task_id and len(tasks) > 1:
            self.send_error(500,
                            message='Founded multiple tasks with the same ID.')
            return
        elif task_id and not tasks:
            self.send_error(400, message='Task is not found.')
            return

        for task in tasks:
            task['result'] = json_decode(task['result'])
            task['status'] = TaskStatus(task['status']).name
            for date_field in ('created', 'started', 'finished'):
                if task[date_field]:
                    task[date_field] = isoformat(task[date_field])
        self.finish(json_encode(tasks[0] if task_id else tasks))
