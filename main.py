import requests as req
from config import Config
from requests.auth import HTTPBasicAuth


class Projects(dict):
    def __init__(self):
        super().__init__()
        resp = req.get(Config.REDMINE_URL+'/projects.json?limit=500', auth=HTTPBasicAuth(Config.LOGIN, Config.PASSWORD))
        # TODO перенести классы по логированию
        print(resp.json())
        if resp.status_code == 200:
            for pr in resp.json()['projects']:
                if list(filter(lambda x: x['name'] == 'Redmine Api' and x['value'] == '1', pr['custom_fields'])):
                    self[pr['identifier']] = Project(id=pr['id'],
                                                     name=pr['name'],
                                                     identifier=pr['identifier'],
                                                     description=pr['description'],
                                                     status=pr['status'],
                                                     custom_fields=pr['custom_fields']
                                                     )
        else:
            print(f'Projects.INIT at {resp.headers["Date"]}: {resp.headers["Status"]}')


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
        self.status = kwargs.get('status')
        self.custom_fields = {i['name']: CustomAttr(id=i['id'],
                                                    name=i['name'],
                                                    value=i['value'])
                              for i in kwargs.get('custom_fields')}


test = Projects()
print(test['mortgage'].custom_fields)
