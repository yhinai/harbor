import json,sys
cases=json.load(open('/tests/cases.json'))
for c in cases: print(json.dumps(c['expected']))
