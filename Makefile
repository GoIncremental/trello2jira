conv:
    iconv -c -f utf-8 -t ascii trello_board_features.json > trello_board_features.ascii.json

test:
    py.test

run:
    python trello2jira.py
