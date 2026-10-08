"""Local checker and interpreter entry point."""
import argparse,json,sys
from pathlib import Path
from language import load,InvalidProgram,StaticError
from checker import check
from interpreter import run

def evaluate(text):
    try:p=load(text)
    except (InvalidProgram,TypeError,ValueError,RecursionError) as e:return {'accepted':False,'status':'invalid_program','message':str(e)}
    try:check(p)
    except StaticError as e:return {'accepted':False,'status':'static_error','message':str(e)}
    try:result=run(p)
    except (KeyError,InvalidProgram) as e:return {'accepted':True,'status':'other_runtime_error','message':str(e)}
    result['accepted']=True
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('program');args=ap.parse_args()
    result=evaluate(Path(args.program).read_text());print(json.dumps(result,indent=2))
    sys.exit(0 if result['accepted'] and result['status']=='type_error' else 1)
