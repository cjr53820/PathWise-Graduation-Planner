"""PathWise educational demo server. Run: python app.py"""
import json, os, secrets, hmac, hashlib, time, re, threading
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from engine import STUDENTS, USERS, audit, timeline, CATALOG, completed_codes
ROOT=Path(__file__).resolve().parent
HOST='127.0.0.1'; PORT=int(os.environ.get('PATHWISE_PORT','8765'))
# All records are synthetic classroom data. Runtime comments disappear on restart.
SESSIONS={}; NOTES={}; LOCK=threading.RLock(); SESSION_AGE=1800
HASHES={u:hashlib.pbkdf2_hmac('sha256',obj['password'].encode(),u.encode(),200000) for u,obj in USERS.items()}

def authenticate(username,password):
 username=username.strip().lower() if isinstance(username,str) else ''
 if username not in USERS or not isinstance(password,str): return None
 guess=hashlib.pbkdf2_hmac('sha256',password.encode(),username.encode(),200000)
 return username if hmac.compare_digest(guess,HASHES[username]) else None

def can_read(username,student_id):
 user=USERS.get(username,{}); stu=STUDENTS.get(student_id)
 return bool(stu and ((user.get('role')=='student' and user.get('student_id')==student_id) or (user.get('role')=='advisor' and student_id in user.get('assigned',[]))))

def public_user(username):
 u=USERS[username]; return {'username':username,'display':u['display'],'role':u['role'],'student_id':u.get('student_id'),'assigned':u.get('assigned',[])}

def public_student(sid):
 s=STUDENTS[sid]; return {k:s[k] for k in ('id','name','major','target','completed','transfers','electives','advisor')}

class Handler(BaseHTTPRequestHandler):
 def log_message(self,fmt,*args):
  # avoid logging passwords, tokens and personal information
  print('[PathWise]',self.command, self.path.split('?')[0], self.address_string())
 def send(self,status,data,ctype='application/json',headers=None):
  payload=json.dumps(data).encode() if ctype=='application/json' else data
  self.send_response(status); self.send_header('Content-Type',ctype+'; charset=utf-8'); self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff'); self.send_header('X-Frame-Options','DENY'); self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
  for k,v in (headers or {}).items(): self.send_header(k,v)
  self.send_header('Content-Length',str(len(payload))); self.end_headers(); self.wfile.write(payload)
 def body(self):
  try:
   n=int(self.headers.get('Content-Length','0'))
   if n>15000: raise ValueError('Request is too large.')
   obj=json.loads(self.rfile.read(n))
   if not isinstance(obj,dict): raise ValueError('Invalid request.')
   return obj
  except (ValueError,json.JSONDecodeError): raise ValueError('Please provide valid form data.')
 def session(self):
  c=SimpleCookie()
  try:c.load(self.headers.get('Cookie',''))
  except Exception:return None
  token=c['pw_session'].value if 'pw_session' in c else ''
  with LOCK:
   row=SESSIONS.get(token)
   if not row: return None
   if time.monotonic()-row['created']>SESSION_AGE: SESSIONS.pop(token,None); return None
   return (token,row)
 def auth(self,csrf=False):
  sess=self.session()
  if not sess: self.send(401,{'error':'Please sign in first.'}); return None
  if csrf and not hmac.compare_digest(self.headers.get('X-CSRF-Token',''),sess[1]['csrf']):
   self.send(403,{'error':'Security check failed. Refresh or sign in again.'});return None
  return sess
 def do_GET(self):
  path=urlparse(self.path).path
  if path=='/':
   self.send(200,(ROOT/'index.html').read_bytes(),'text/html'); return
  if path=='/style.css':self.send(200,(ROOT/'style.css').read_bytes(),'text/css'); return
  if path=='/frontend.js':self.send(200,(ROOT/'frontend.js').read_bytes(),'application/javascript'); return
  if path=='/api/health':self.send(200,{'status':'ok','demo':True});return
  sess=self.auth();
  if not sess:return
  username=sess[1]['user']; u=USERS[username]
  if path=='/api/me': self.send(200,{'user':public_user(username),'csrf':sess[1]['csrf']});return
  if path=='/api/students':
   ids=([u['student_id']] if u['role']=='student' else u['assigned'])
   self.send(200,{'students':[{'id':sid,'name':STUDENTS[sid]['name'],'target':STUDENTS[sid]['target']} for sid in ids]});return
  match=re.fullmatch(r'/api/student/(s\d+)',path)
  if match:
   sid=match.group(1)
   if not can_read(username,sid):self.send(403,{'error':'You do not have access to this student.'});return
   with LOCK: notes=list(NOTES.get(sid,[]))
   self.send(200,{'student':public_student(sid),'audit':audit(STUDENTS[sid]),'timeline':timeline(STUDENTS[sid]),'notes':notes});return
  self.send(404,{'error':'Page not found.'})
 def do_POST(self):
  path=urlparse(self.path).path
  try: data=self.body()
  except ValueError as e:self.send(400,{'error':str(e)});return
  if path=='/api/login':
   username=authenticate(data.get('username',''),data.get('password',''))
   if not username:self.send(401,{'error':'Incorrect username or password.'});return
   token=secrets.token_urlsafe(32);csrf=secrets.token_urlsafe(24)
   with LOCK:SESSIONS[token]={'user':username,'csrf':csrf,'created':time.monotonic()}
   self.send(200,{'user':public_user(username),'csrf':csrf},headers={'Set-Cookie':f'pw_session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age={SESSION_AGE}'});return
  sess=self.auth(csrf=True)
  if not sess:return
  username=sess[1]['user']
  if path=='/api/logout':
   with LOCK:SESSIONS.pop(sess[0],None)
   self.send(200,{'ok':True},headers={'Set-Cookie':'pw_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0'});return
  if path=='/api/scenario':
   sid=data.get('student_id','')
   if not can_read(username,sid):self.send(403,{'error':'You cannot view this student.'});return
   try:
    load=data.get('load',3)
    if type(load) is not int: raise ValueError('Courses per term must be a whole number.')
    result=timeline(STUDENTS[sid],load,data.get('proposed',[]))
   except ValueError as e:self.send(400,{'error':str(e)});return
   self.send(200,{'scenario':result,'audit':audit(STUDENTS[sid]),'record_changed':False});return
  if path=='/api/note':
   sid=data.get('student_id','');msg=data.get('message','')
   if USERS[username]['role']!='advisor' or not can_read(username,sid):self.send(403,{'error':'Only the assigned advisor can add recommendations.'});return
   if not isinstance(msg,str) or not (3<=len(msg.strip())<=400):self.send(400,{'error':'Please enter a recommendation between 3 and 400 characters.'});return
   note={'advisor':USERS[username]['display'],'text':msg.strip(),'date':datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
   with LOCK:NOTES.setdefault(sid,[]).append(note)
   self.send(201,{'note':note});return
  self.send(404,{'error':'Route not found.'})

def run():
 server=ThreadingHTTPServer((HOST,PORT),Handler)
 print(f'PathWise demo: http://{HOST}:{PORT} | CTRL+C to exit')
 server.serve_forever()
if __name__=='__main__':run()
