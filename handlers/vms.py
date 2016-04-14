from tornado import gen
from tornado.escape import json_encode

import commands
from decorators import authenticated
from handlers.base import BaseHandler
from schemas import TaskResponseSchema, DomainRequestSchema
from tasks import Task


class DomainHandler(BaseHandler):
    @authenticated
    @gen.coroutine
    def get(self, domain_id=None):
        task = Task(commands.start, self.get_current_user(), self.application,
                    params={'domain_id': domain_id, })
        yield task.add_to_queue()
        self.finish(TaskResponseSchema().dumps(task).data)

    @authenticated
    @gen.coroutine
    def post(self):
        data, errors = DomainRequestSchema(exclude=('id',)).loads(
            self.request.body.decode('utf-8'))

        if errors:
            self.send_error(400, message='Wrong input parameters',
                            errors=errors)
            return

        task = Task(commands.create_domain, self.get_current_user(),
                    self.application, params=data)
        yield task.add_to_queue()
        self.finish(TaskResponseSchema().dumps(task).data)


class NodeHandler(BaseHandler):
    @authenticated
    @gen.coroutine
    def get(self, node_id=None):
        task = Task(commands.get_nodes_info, self.get_current_user(),
                    self.application, params={'node_id': node_id})
        yield task.add_to_queue()
        self.finish(TaskResponseSchema().dumps(task).data)
