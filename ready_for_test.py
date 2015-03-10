import sys
import datetime
from collections import namedtuple

import tinys3
import requests
from requests.auth import HTTPBasicAuth
from jinja2 import FileSystemLoader, Environment
from lxml import objectify

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ENCODING = 'utf-8'
S3_ACCESS_KEY='AKIAJ7YQJ3VHYEBRGTHQ'
S3_SECRET_KEY='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' 

def render_from_template(directory, template_name, **kwargs):
    loader = FileSystemLoader(directory)
    env = Environment(loader=loader)
    template = env.get_template(template_name)
    return template.render(**kwargs)

def load_results():
    with open('/home/ben/src/github.com/rethought/soxmas/robot/output/output.xml', 'r') as output:
        return objectify.parse(output)
        

def test_passed(jira_number, results):
    for v in results.findall("//test"):
        if jira_number in v.get('name'):
            for s in v.getchildren():
                if s.get('status') == 'PASS':
                    return True


def get_jiras(status="Ready For Test"):
    errors = []
    headers = {'Content-Type': 'application/json'}
    jql_url = 'https://sainsburys.jiraoncloud.com/rest/api/2/search'
    params = dict(jql='component="10100"&status="{}"'.format(status))
    auth = HTTPBasicAuth('ben.hughes', 'icbiatwt2')
    logger.info('Querying JIRA...')
    response = requests.get(url=jql_url, params=params, auth=auth, headers=headers, verify=False)
    logger.info('Calling {}'.format(response.url))
    if response.status_code == 200:
        return response.json()
    else:
        logger.fatal('Bad shit happened: {}'.format(response.content))
        exit()

if __name__ == '__main__':
    results = load_results()
    status = "Ready For Test"
    rft = get_jiras(status=status)
    issues = []
    Issue = namedtuple('Issue', ['key', 'summary', 'acceptance_criteria', 'passed'])
    for issue in rft.get('issues'):
        issue_id = issue.get('key')
        fields = issue.get('fields')
        summary = fields.get('summary')
        passed = test_passed(issue_id, results)

        def get_acceptance_criteria(acceptance_criteria_text):
            """ Gets all none empty text from the JIRA description """
            if acceptance_criteria_text:
                ac = [p.strip() for p in acceptance_criteria_text.split('\n')]
                return filter(lambda x: x != '', ac) 
        
        i = Issue(key=issue_id, summary=summary, passed=passed,
                  acceptance_criteria=get_acceptance_criteria(fields.get('description')))
        print 'Issue:{} passed={}'.format(i.key, i.passed)
        issues.append(i)
    num_passes = len(filter(lambda x: x.passed, issues))
    num_issues = len(issues)
    test_coverage = num_passes/num_issues*100
    print '{} passed out of {} - {} coverage.'.format(num_passes, num_issues, test_coverage)

    with open('html/report.html', 'w') as report:
        updated_at = datetime.datetime.now().strftime('%Y/%m/%d %H:%M')
        output = render_from_template('templates', 'report.tmpl', 
                                      **dict(issues=issues, status=status, 
                                             updated_at=updated_at))
        report.write(output.encode(ENCODING))
        
    if sys.argv[1] == '--publish':
        with open('html/report.html', 'rb') as report:
            logging.info("Uploading to S3...")
            conn = tinys3.Connection(S3_ACCESS_KEY,S3_SECRET_KEY, 
                                    tls=True, 
                                    default_bucket='soxmas',
                                    endpoint='s3-eu-west-1.amazonaws.com')
            logging.info(conn.upload('html/report.html', report))
            # logging.info('Making public...')
            # conn.update_metadata('/html/report.html', public=True)