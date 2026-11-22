# Testing summary

The source project was checked locally with Python 3.13 and Node:

| Check | Result |
|---|---|
| `node --check frontend.js` | Passed |
| `python -m unittest discover -v` | 20/20 passed |
| `python http_smoke.py` | 16/16 passed |
| Scripted browser demonstration | Recorded; MP4 and screenshots in Blackboard ZIP |

The HTTP checks verify unauthorized (401/403), invalid inputs (400), CSRF, temporary planning, record isolation, advisor recommendations and logout. All records are fictional.

The GitHub Actions workflow reruns JavaScript syntax, unit, and HTTP checks on pushes and pull requests. Check the Actions tab for GitHub-hosted results.

These checks do not prove production readiness, real university data integration, or broader browser compatibility. The team should still conduct and document independent manual UAT.
