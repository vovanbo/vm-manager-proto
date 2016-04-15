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
        user = self.get_current_user()
        task = Task(commands.get_domains_info, user, self.application,
                    params={'domain_id': domain_id, 'user_id': user['id']})
        yield task.add_to_queue()
        self.finish(TaskResponseSchema().dumps(task).data)

    @authenticated
    @gen.coroutine
    def post(self):
        data, errors = DomainRequestSchema(exclude=('uuid', 'state')).loads(
            self.request.body.decode('utf-8'))

        if errors:
            self.send_error(400, message='Wrong input parameters',
                            errors=errors)
            return

        user = self.get_current_user()
        data.update({'user_id': user['id']})
        task = Task(commands.create_domain, user, self.application,
                    params=data)
        yield task.add_to_queue()
        self.finish(TaskResponseSchema().dumps(task).data)

    @authenticated
    @gen.coroutine
    def patch(self, domain_id=None):
        if domain_id is None:
            self.send_error(400, message='Domain ID must be passed in URI.')
            return

        data, errors = DomainRequestSchema(only=('state',)).loads(
            self.request.body.decode('utf-8'))

        if errors:
            self.send_error(400, message='Wrong input parameters',
                            errors=errors)
            return

        user = self.get_current_user()
        data.update({'domain_id': domain_id, 'user_id': user['id']})
        # TODO: Support changing any parameters, not only 'state'
        task = Task(commands.change_domain_state, user, self.application,
                    params=data)
        yield task.add_to_queue()
        self.finish(TaskResponseSchema().dumps(task).data)

    @authenticated
    @gen.coroutine
    def delete(self, domain_id=None):
        if domain_id is None:
            self.send_error(400, message='Domain ID must be passed in URI.')
            return

        user = self.get_current_user()
        task = Task(commands.delete_domain, user, self.application,
                    params={'domain_id': domain_id, 'user_id': user['id']})
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
