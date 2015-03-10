import os
import json
import requests
from requests.auth import HTTPBasicAuth
from jinja2 import FileSystemLoader, Environment

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

loader = FileSystemLoader('templates')
env = Environment(loader=loader)


class TrelloCard(object):
    def __init__(self, card):
        self.name = card.get('name')
        self.url = card.get('shortUrl')
        self.description = "Migrated from {} .".format(self.url)

    def __repr__(self):
        return '<TrelloCard {}>'.format(self.url)

    def render_as_jira_story(self, template):
        kwargs = dict(project_key='ISSA', card_name=self.name, card_description=self.description)
        logger.info('Rendering trello card to JIRA Story...')
        return template.render(**kwargs)


def trello_card_to_jira_issue_generator(trello_board, template):
    all_cards = trello_board.get('cards')
    logger.info("Processing {} cards...".format(len(all_cards)))
    for card in all_cards:
        tc = TrelloCard(card)
        yield tc.render_as_jira_story(template)


def load_trello_export(trello_export):
    logger.info('Loading {}...'.format(trello_export))
    with open(trello_export, 'r') as trello_board:
        tb = json.load(trello_board)
        return tb


def create_jira_issue(story):
    errors = []
    headers = {'Content-Type': 'application/json'}
    issue_url = 'https://sainsburys.jiraoncloud.com/rest/api/2/issue/'
    auth = auth=HTTPBasicAuth('ben.hughes', 'icbiatwt2')
    logger.info('Creating Trello card in JIRA...')
    response = requests.post(url=issue_url, auth=auth, data=story, headers=headers, verify=False)
    return response


if __name__ == '__main__':
    template = env.get_template('jira.story.tmpl')
    trello_board = load_trello_export('trello_board_features.ascii.json')
    for jira_story in trello_card_to_jira_issue_generator(trello_board, template):
        print jira_story
        response = create_jira_issue(jira_story)
        assert response.status_code == 200
        
