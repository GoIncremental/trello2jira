rft = [
	   1141,
	   210,
	   1087,
	   336,
	   266,
	   307,
	   1285,
	   664,
	   1280,
	   1264,
	   270,
	   1257,
	   334,
	   1148,
	   281,
	   324,
	   303
]

T = "project=CFTO and id="
p = ''
for x in rft:
	p = p.join('{},'.format(x))

print p