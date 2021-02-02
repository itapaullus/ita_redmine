import requests as req
from config import Config
from requests.auth import HTTPBasicAuth
import pandas as pd


def send_request(**kwargs):
    resp = req.get(url=Config.REDMINE_URL + '/projects.json?limit=500',
                   auth=HTTPBasicAuth(Config.LOGIN, Config.PASSWORD)
                   # , params=kwargs.get('params')
                   )
    if resp.status_code == 200:
        return resp
    else:
        print(
            f'Error: send_request to {kwargs.get("url")} at {resp.headers["Date"]}: {resp.headers["Status"]}. {resp.text}')


class Projects(dict):
    def __init__(self):
        super().__init__()
        resp = send_request(url=Config.REDMINE_URL + '/projects.json?limit=500')
        # print(f'debug type={type(resp)}')
        # TODO перенести классы по логированию
        if resp:
            for pr in resp.json()['projects']:
                if list(filter(lambda x: x['name'] == 'Redmine Api' and x['value'] == '1', pr['custom_fields'])):
                    self[pr['identifier']] = Project(id=pr['id'],
                                                     name=pr['name'],
                                                     identifier=pr['identifier'],
                                                     description=pr['description'],
                                                     status=pr['status'],
                                                     custom_fields=pr['custom_fields']
                                                     )


class CustomAttr:
    def __init__(self, **kwargs):
        if kwargs.get('custom_fields'):
            pass
        else:
            self.id = kwargs.get('id')
            self.name = kwargs.get('name')
            self.value = kwargs.get('value')

    def __repr__(self):
        return f'(CustomAttr: id:{self.id}; name:{self.name}; value:{self.value})'


class Project:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.identifier = kwargs.get('identifier')
        self.description = kwargs.get('description')
        self.homepage = kwargs.get('homepage')
        self.parent = kwargs.get('parent')
        self.status = kwargs.get('status')
        self.custom_fields = {i['name']: CustomAttr(id=i['id'],
                                                    name=i['name'],
                                                    value=i['value'])
                              for i in kwargs.get('custom_fields')}
        self.users = {}

    def __repr__(self):
        return f'Project: {self.name}\n' \
               f'   id: {self.id}\n' \
               f'   identifier: {self.identifier}\n'

    def get_users(self):
        resp = req.get(Config.REDMINE_URL + f'/projects/{self.id}/memberships.json',
                       auth=HTTPBasicAuth(Config.LOGIN, Config.PASSWORD))
        for i in resp.json()['memberships']:
            try:
                new_id = i['user']['id']
                new_user = User(id=new_id, name=i['user']['name'])
                self.users[new_user.login] = new_user
            except:
                pass


class User:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        if kwargs.get('login') and kwargs.get('firstname') and kwargs.get('lastname') and kwargs.get(
                'mail'):  # если данные уже пришли, то заполняем
            self.login = kwargs.get('login')
            self.firstname = kwargs.get('firstname')
            self.lastname = kwargs.get('lastname')
            self.mail = kwargs.get('mail')
        else:  # вызываем сервис
            resp = req.get(Config.REDMINE_URL + f'/users.json',
                           auth=HTTPBasicAuth(Config.LOGIN, Config.PASSWORD),
                           params={'name': kwargs.get('name'),
                                   'status': '1'}
                           )
            self.login = resp.json()['users'][0]['login']
            self.firstname = resp.json()['users'][0]['firstname']
            self.lastname = resp.json()['users'][0]['lastname']
            self.mail = resp.json()['users'][0]['mail']

    def __repr__(self):
        return f'User: {self.firstname} {self.lastname} ({self.login})'

    def get_open_tasks(self):
        resp = req.get(Config.REDMINE_URL + f'/issues.json',
                       auth=HTTPBasicAuth(Config.LOGIN, Config.PASSWORD),
                       params={'assigned_to_id': self.id}
                       )
        self.tasks = {}
        for i in resp.json()['issues']:
            self.tasks[i['id']] = Task(id=i['id'],
                                       project=i.get('project', {}),
                                       tracker=i.get('tracker', {}),
                                       status=i.get('status', {}),
                                       priority=i.get('priority', {}),
                                       author=i.get('author', {}),
                                       assigned_to=i.get('assigned_to', {}),
                                       parent=i.get('parent', {}),
                                       subject=i.get('subject'),
                                       description=i.get('description'),
                                       start_date=i.get('start_date'),
                                       due_date=i.get('due_date'),
                                       done_ratio=i.get('done_ratio'),
                                       is_private=i.get('is_private'),
                                       estimated_hours=i.get('estimated_hours'),
                                       custom_fields=i.get('custom_fields'),
                                       created_on=i.get('created_on'),
                                       updated_on=i.get('updated_on'),
                                       closed_on=i.get('closed_on')
                                       )

    def get_data_frame(self):
        data = [[i.id, i.project.get('name'), i.tracker.get('name'), i.status.get('name'), i.priority.get('name'), i.author.get('name'),
                 i.assigned_to.get('name'), i.parent.get('id'), i.subject,
                 i.description, i.start_date, i.due_date, i.done_ratio, i.is_private, i.estimated_hours,
                 i.custom_fields,
                 i.created_on, i.updated_on, i.closed_on] for i in self.tasks.values()]
        # print(data)
        entries = ['id', 'project', 'tracker', 'status', 'priority', 'author', 'assigned_to', 'parent', 'subject',
                   'description', 'start_date', 'due_date', 'done_ratio', 'is_private', 'estimated_hours',
                   'custom_fields', 'created_on', 'updated_on', 'closed_on']
        return pd.DataFrame(data=data, columns=entries)


class Task:
    def __init__(self, **kwargs):
        # print(f'debug id = {kwargs.get("id")}')
        self.id = kwargs.get('id')
        self.project = kwargs.get('project')
        self.tracker = kwargs.get('tracker')
        self.status = kwargs.get('status')
        self.priority = kwargs.get('priority')
        self.author = kwargs.get('author')
        self.assigned_to = kwargs.get('assigned_to')
        self.parent = kwargs.get('parent')
        self.subject = kwargs.get('subject')
        self.description = kwargs.get('description')
        self.start_date = kwargs.get('start_date')
        self.due_date = kwargs.get('due_date')
        self.done_ratio = kwargs.get('done_ratio')
        self.is_private = kwargs.get('is_private')
        self.estimated_hours = kwargs.get('estimated_hours')
        self.custom_fields = kwargs.get('custom_fields')
        self.created_on = kwargs.get('created_on')
        self.updated_on = kwargs.get('updated_on')
        self.closed_on = kwargs.get('closed_on')

    def __repr__(self):
        # print(f'debug repr id = {self.id}')
        return f'Task #{self.id}: subject: {self.subject}'


test = Projects()
test['mortgage'].get_users()
cur = test['mortgage'].users['i.konkin']
cur.get_open_tasks()
"""
:type cur: User
"""


print(cur.tasks)
df = cur.get_data_frame()
print(df.info())
# print(df['tracker'])
pr = df.loc[:, ['tracker', 'start_date', 'updated_on']]
print(pr)
print(pr[pr['start_date'] < pr['updated_on']]['tracker'].count())
