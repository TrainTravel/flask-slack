from pytest import fixture
from flask import Flask

from flask_slack import Slack


class App(object):

    def __init__(self):
        self.app = Flask(__name__)
        self.app.debug = True
        self.slack = Slack(self.app)
        self.app.add_url_rule('/', view_func=self.slack.dispatch)
        self.client = self.app.test_client()


@fixture(scope='module')
def app():
    return App()


def test_request_without_registering_commands(app):
    res = app.client.get('/')
    assert res.status_code == 200
    assert res.data == b'Command None is not found in team None'


def test_registering_commands(app):
    command = 'sing'
    token = 'mytoken'
    team_id = 'MYTEAMID'
    methods = ['POST']
    text = 'little apple'

    get_url = '/?token={0}&team_id={1}&command={2}&text={3}'.format(
        token, team_id, command, text)

    @app.slack.command(command, token, team_id, methods)
    def _sing_a_song(**kwargs):
        lyrics = 'You are my littttle apple...'
        return app.slack.response(lyrics)

    expected_commands = {
        (team_id, command): (_sing_a_song, token, methods, {}),
    }

    assert app.slack._commands == expected_commands

    get_res = app.client.get(get_url)

    assert get_res.status_code == 200
    assert get_res.data == b'GET request is not allowed'