import json, sys
def solve(request):
    raise NotImplementedError("Implement the contract in instruction.md")
if __name__ == '__main__':
    for line in sys.stdin:
        print(json.dumps(solve(json.loads(line))))
