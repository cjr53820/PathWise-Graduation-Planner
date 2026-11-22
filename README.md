# ↗ PathWise — Academic Planning Prototype


**CSC 380 Software Engineering • Norfolk State University**  
**PathWise Development Team:** Christopher Robinson, Anaya Skinner-Edwards, Jomar Supreme

PathWise is a working, local web-app prototype that helps students view academic progress, understand prerequisites, experiment with graduation scenarios, and read advisor recommendations. It also gives assigned advisors a limited view of their students and the ability to leave notes.

> **Classroom demonstration only.** All student records are fictional. The 40-credit degree example and term estimates are illustrative—not NSU catalog data or an official degree audit.

## Core features

| Area | What you can demonstrate |
|---|---|
| Dashboard | Completed credits, remaining requirements, projected graduation |
| Requirements | Completed, ready, blocked, and accepted transfer courses |
| Timeline | Proposed schedule constrained by prerequisites |
| What If? planner | Change semester load or prioritize a course without overwriting records |
| Advisor insights | Role-restricted notes on assigned student records |
| Validation and security | Invalid-course handling, login and session controls, role-based API permission checks |

## Quick start

Requires **Python 3.10+**. No pip dependencies or database installation are necessary.

```bash
python app.py
```
Open **http://127.0.0.1:8765** in your browser. The server listens only on 127.0.0.1 and should not be deployed to the public internet.

| Role | Username | Demo password |
|---|---|---|
| Student — Maya | `maya` | `Demo123!` |
| Student — Daniel | `daniel` | `Demo123!` |
| Advisor — Dr. Rivers | `drivers` | `Demo123!` |
| Advisor — Prof. Parker | `aparker` | `Demo123!` |

The recorded demo video is included in the companion Blackboard ZIP. [Narration script](demo/PathWise_Video_Narration.txt)

## Demo guide

1. Log in as `maya` to review **18/40** sample earned credits.
2. Open **Degree requirements** to see transfer credit and prerequisite labels.
3. Open **Graduation timeline** to see the recommended course order.
4. Open **What If? planner**, set **4 courses per semester**, select **CSC 301**, and calculate. Notice that official credits remain **18/40**.
5. Select **CSC 490** prematurely and recalculate to see a prerequisite error.
6. Open **Advisor insights** as Maya: students can see notes but not post them.
7. Sign out, log in as `drivers`, open **Advisor insights**, leave a recommendation, and switch between Maya and Daniel.
8. Sign back in as Maya to see the saved note for the current server session.

## Verification

```bash
node --check frontend.js
python -m unittest discover -v
python http_smoke.py
```

After fixing an early JavaScript syntax issue, the suite contains **20 passing unit tests** and **16 passing HTTP workflow checks**, covering input validation, authorization, planning isolation, transfer credits, and session behavior. CI also checks JavaScript syntax. See [`docs/testing`](docs/testing) for captured console results; UI screenshots and the video are in the separate Blackboard ZIP.

## System architecture

- `app.py`: Python standard-library HTTP server, cookie sessions and JSON API
- `engine.py`: academic audit and course-sequencing logic
- `index.html`, `style.css`, `frontend.js`: responsive application interface
- `data_schema.json`: sample data structure; live data is held in memory, not SQL
- `test_pathwise.py`: unit tests
- `http_smoke.py`: API workflow checks
- `docs/diagrams`: diagrams for the design report

## Important limitations

- **No actual university records, production deployment, or external API.**
- Advisor notes and sessions only persist while the server is running.
- Simplified curriculum, not official registration or degree rules.
- Demo accounts are public examples; there is no TLS or production identity provider.
- Real deployment would need HTTPS, database access control, university authentication, and wider testing.

## AI-use disclosure

Generative AI helped draft and implement substantial parts of the prototype, tests, documentation and presentation. The team must review and verify the result, explain the source code, and give accurate individual-contribution and peer-evaluation statements. Do not claim a feature was created, reviewed or tested by a teammate unless it actually was.

## Repository link

https://github.com/cjr53820/PathWise-Graduation-Planner