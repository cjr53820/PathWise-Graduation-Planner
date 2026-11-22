# Frontend and browser walkthrough evidence

After correcting the JavaScript callback syntax in the initial draft:
- `node --check frontend.js`: passed locally.
- `python -m unittest discover -v`: 20/20 tests passed locally.
- `python http_smoke.py`: 16/16 HTTP checks passed locally.

A 95-second walkthrough was recorded from the actual HTML, CSS and JavaScript frontend communicating with a running Python backend. Browser navigation to localhost was blocked in the recording environment, so the recorder used an in-process bridge for real API responses—not fabricated data.

**Recorded steps:** Maya logs in; views 18/40 credits, transfer and blocked classes; reviews the course timeline; runs a four-course What If? scenario without changing official credits; receives prerequisite validation for CSC 490; observes student permissions; Dr. Rivers signs in and writes a note to an assigned student; Maya later sees that note; advisor checks Daniel's timeline.

The MP4 and screenshots are included in the Blackboard submission ZIP. This is a scripted demonstration, **not independent user acceptance testing**. The data and advisors are fictional, and advisor notes are kept only in memory.
