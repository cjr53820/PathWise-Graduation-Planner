"""PathWise classroom demo: deterministic degree audit and term planner."""
from copy import deepcopy

CATALOG = {
 'ENG 101': {'title':'College Composition I','credits':3,'prereqs':[]},
 'ENG 102': {'title':'College Composition II','credits':3,'prereqs':['ENG 101']},
 'MTH 161': {'title':'Precalculus','credits':3,'prereqs':[]},
 'MTH 251': {'title':'Calculus I','credits':4,'prereqs':['MTH 161']},
 'CSC 201': {'title':'Intro to Programming','credits':3,'prereqs':[]},
 'CSC 202': {'title':'Programming II','credits':3,'prereqs':['CSC 201']},
 'CSC 301': {'title':'Data Structures','credits':3,'prereqs':['CSC 202']},
 'CSC 380': {'title':'Software Engineering','credits':3,'prereqs':['CSC 301']},
 'CSC 490': {'title':'Senior Capstone','credits':3,'prereqs':['CSC 380']},
 'CYS 210': {'title':'Intro to Cybersecurity','credits':3,'prereqs':['CSC 201']},
 'NET 310': {'title':'Computer Networks','credits':3,'prereqs':['CSC 202']},
 'IT 400': {'title':'Information Technology Seminar','credits':3,'prereqs':[]},
 'IT ELEC': {'title':'Approved IT Elective (demo)','credits':3,'prereqs':[]},
}
REQUIRED = ['ENG 101','ENG 102','MTH 161','MTH 251','CSC 201','CSC 202','CSC 301','CSC 380','CSC 490','CYS 210','NET 310','IT 400','IT ELEC']
# This is an intentionally small 40-credit illustrative program, NOT a university catalog.
assert sum(CATALOG[c]['credits'] for c in REQUIRED)==40
TARGET_CREDITS=40
STUDENTS = {
 's1001': {'id':'s1001','name':'Maya Thompson','major':'Information Technology','target':'Spring 2027','completed':['ENG 101','MTH 161','CSC 201','CSC 202','CYS 210'], 'transfers':[{'course':'ENG 102','source':'Northern Virginia Community College','credits':3}], 'electives':0,'advisor':'drivers'},
 's1002': {'id':'s1002','name':'Daniel Brooks','major':'Information Technology','target':'Spring 2027','completed':['ENG 101','MTH 161','CSC 201'], 'transfers':[], 'electives':0,'advisor':'drivers'},
 's1003': {'id':'s1003','name':'Alex Morgan','major':'Information Technology','target':'Fall 2027','completed':['ENG 101','MTH 161','CSC 201','CSC 202'], 'transfers':[], 'electives':0,'advisor':'aparker'},
}
USERS = {
 'maya': {'password':'Demo123!','role':'student','student_id':'s1001','display':'Maya Thompson'},
 'daniel': {'password':'Demo123!','role':'student','student_id':'s1002','display':'Daniel Brooks'},
 'drivers': {'password':'Demo123!','role':'advisor','display':'Dr. Rivers','assigned':['s1001','s1002']},
 'aparker': {'password':'Demo123!','role':'advisor','display':'Prof. Parker','assigned':['s1003']},
}
TERMS=['Fall 2026','Spring 2027','Fall 2027','Spring 2028','Fall 2028','Spring 2029','Fall 2029','Spring 2030','Fall 2030','Spring 2031']

def normalize_course(c):
 if not isinstance(c,str): raise ValueError('Enter a valid course code.')
 return ' '.join(c.strip().upper().split())

def parse_course_list(value):
 if not isinstance(value,list): raise ValueError('Course selection must be a list.')
 result=[]
 for raw in value:
  code=normalize_course(raw)
  if code not in CATALOG: raise ValueError(f'{code or "Blank course"} is not in the demo catalog.')
  if code in result: raise ValueError(f'{code} was entered more than once.')
  result.append(code)
 return result

def completed_codes(student):
 # Set ensures transfer-equivalent + completed course never double-count.
 return set(student['completed']) | {t['course'] for t in student['transfers'] if t['course'] in CATALOG}

def audit(student):
 done=completed_codes(student)
 credit=sum(CATALOG[c]['credits'] for c in done if c in REQUIRED)+student.get('electives',0)
 # transfer counted under the same requirement, not as additional duplicated credit
 rows=[]
 for code in REQUIRED:
  pre=CATALOG[code]['prereqs']; missing=[p for p in pre if p not in done]
  transfer=next((t for t in student['transfers'] if t['course']==code),None)
  status='Transfer' if transfer else ('Completed' if code in done else ('Blocked' if missing else 'Ready'))
  rows.append({'code':code,'name':CATALOG[code]['title'],'credits':CATALOG[code]['credits'],'status':status,'missing':missing,'source':transfer['source'] if transfer else None})
 return {'earned':credit,'total':TARGET_CREDITS,'remaining':max(0,TARGET_CREDITS-credit),'rows':rows,'complete':len(done.intersection(REQUIRED)),'required':len(REQUIRED)}

def timeline(student,load=3, proposed=None):
 if not isinstance(load,int) or not (1<=load<=5): raise ValueError('Courses per term must be between 1 and 5.')
 # What If? calculations use copies, never mutate student record.
 copied=deepcopy(student)
 done=completed_codes(copied)
 proposed=parse_course_list(proposed or [])
 for c in proposed:
  if c in done: raise ValueError(f'{c} is already completed or transferred.')
  miss=[p for p in CATALOG[c]['prereqs'] if p not in done]
  if miss: raise ValueError(f'{c} needs {", ".join(miss)} first.')
 scheduled=[]; remaining=[c for c in REQUIRED if c not in done]
 for term in TERMS:
  ready=[c for c in remaining if set(CATALOG[c]['prereqs']).issubset(done)]
  # Highlight scenario courses where feasible, without breaking prerequisites.
  ready.sort(key=lambda c:(0 if c in proposed else 1, REQUIRED.index(c)))
  chosen=ready[:load]
  if not chosen: break
  scheduled.append({'term':term,'courses':[{'code':c,'name':CATALOG[c]['title']} for c in chosen]})
  done.update(chosen)
  remaining=[c for c in remaining if c not in chosen]
 if remaining: raise ValueError('Unable to schedule remaining courses within demo term range.')
 finish=scheduled[-1]['term'] if scheduled else TERMS[0]
 delay=TERMS.index(finish)>TERMS.index(student['target']) if student['target'] in TERMS else False
 return {'terms':scheduled,'finish':finish,'target':student['target'],'delay':delay,'proposed':proposed,'notice':'Illustrative plan only — not an official degree audit.','remaining_elective_credits': 0}
