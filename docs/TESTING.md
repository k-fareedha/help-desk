# Testing and Validation

## Manual checks
- Start backend and frontend, verify ticket creation and list refresh.
- Submit empty ticket and verify browser validation.
- Without an API key, verify assistant shows configuration guidance.
- With a valid key, verify assistant returns a response.
- Inspect browser network errors and backend logs.

## Automated checks
From project root after installing backend dependencies:
```bash
pytest tests -q
```
From frontend after installing dependencies:
```bash
npm run build
```

## Results
Not executed as part of the starter packaging. Record actual commands, dates, pass/fail counts, and screenshots here after running.
