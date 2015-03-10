from lxml import etree
from lxml import objectify

with open('/home/ben/src/github.com/rethought/soxmas/robot/output/output.xml', 'r') as output:
	tree = objectify.parse(output)
	for v in tree.findall("//test"):
		print v.get('name')
		for s in v.getchildren():
			if s.get('status') == 'PASS':
				print s
		