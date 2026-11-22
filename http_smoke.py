"""Real HTTP workflow smoke test; uses stdlib only."""
import urllib.request,urllib.error,subprocess,sys,time,json,pathlib,http.cookiejar
ROOT=pathlib.Path(__file__).parent
server=subprocess.Popen([sys.executable,'app.py'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
jar=http.cookiejar.CookieJar(); opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
results=[]
def req(path,data=None,csrf=None):
 h={'Content-Type':'application/json'}
 if csrf:h['X-CSRF-Token']=csrf
 r=urllib.request.Request('http://127.0.0.1:8765'+path,data=json.dumps(data).encode() if data is not None else None,headers=h)
 try:
  with opener.open(r,timeout=5) as f:return f.status,json.load(f)
 except urllib.error.HTTPError as e:return e.code,json.load(e)
def check(name,actual,expected):
 result=actual==expected;results.append((name,result,actual));print(('PASS' if result else 'FAIL'),name,'got',actual,'expected',expected)
try:
 for i in range(30):
  try:req('/api/health');break
  except Exception:time.sleep(.2)
 check('Anonymous student request rejected',req('/api/student/s1001')[0],401)
 status,data=req('/api/login',{'username':'maya','password':'Demo123!'})
 check('Student demo login',status,200);csrf=data['csrf']
 check('Student sees own dashboard',req('/api/student/s1001')[0],200)
 check('Student cannot open another student',req('/api/student/s1002')[0],403)
 check('What If requires CSRF header',req('/api/scenario',{'student_id':'s1001','load':4,'proposed':[]})[0],403)
 status,scenario=req('/api/scenario',{'student_id':'s1001','load':4,'proposed':['CSC 301']},csrf)
 check('Valid planning scenario',status,200);check('Record unchanged after planning',scenario.get('record_changed'),False)
 check('Blocked prerequisite rejected',req('/api/scenario',{'student_id':'s1001','load':4,'proposed':['CSC 490']},csrf)[0],400)
 check('Bad course rejected',req('/api/scenario',{'student_id':'s1001','load':4,'proposed':['CSC 999']},csrf)[0],400)
 check('Student cannot add advisor note',req('/api/note',{'student_id':'s1001','message':'take CSC 301'},csrf)[0],403)
 check('Logout',req('/api/logout',{},csrf)[0],200)
 check('Old session invalidated',req('/api/student/s1001')[0],401)
 status,data=req('/api/login',{'username':'drivers','password':'Demo123!'})
 check('Advisor demo login',status,200);csrf=data['csrf']
 check('Assigned advisor may add note',req('/api/note',{'student_id':'s1001','message':'Take CSC 301 next term.'},csrf)[0],201)
 check('Advisor cannot read unassigned student',req('/api/student/s1003')[0],403)
 check('Advisor notes visible on assigned record',len(req('/api/student/s1001')[1]['notes']),1)
finally:
 server.terminate();server.wait(timeout=5)
evidence=(ROOT/'docs'/'testing') if (ROOT/'docs'/'testing').exists() else (ROOT.parent/'Testing_Evidence')
evidence.mkdir(parents=True,exist_ok=True)
report=evidence/'http_smoke_results.txt'
report.write_text('PathWise live HTTP smoke test\n'+ '\n'.join(f"{'PASS' if ok else 'FAIL'} | {name} | Actual: {actual}" for name,ok,actual in results)+f'\n\n{sum(ok for _,ok,_ in results)}/{len(results)} passed\n')
if not all(ok for _,ok,_ in results):sys.exit(1)
