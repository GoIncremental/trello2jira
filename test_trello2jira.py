import pytest
from mock import Mock, MagicMock, patch

from httmock import HTTMock, response, all_requests
from trello2jira import TrelloCard, create_jira_issue


@pytest.fixture
def mock_tc():
    mock_card =  MagicMock(spec=dict)
    return TrelloCard(mock_card)

@all_requests
def response_content(url, request):
    headers = {'content-type': 'application/json'}
    content = {'some': 'data'}
    return response(200, content, headers, None, 5, request)

def test_trellocard():
    mock_card = MagicMock(spec=dict)
    tc = TrelloCard(mock_card)
    assert mock_card.get.called_once_with('shortUrl')
    assert mock_card.get.called_once_with('name')
    assert tc.description.startswith('Migrated from')
    assert str(tc).startswith('<TrelloCard ')


def test_trellocard_render_as_jira_story(mock_tc):
    mock_template = Mock()
    mock_tc.render_as_jira_story(mock_template)
    assert mock_template.render.called


def test_create_jira():
    with HTTMock(response_content):
        mock_story = MagicMock(spec=dict)
        response = create_jira_issue(mock_story)
        assert response.json().get('some') == 'data'
