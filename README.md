# URL-shortener
URL shortener - project to learn new tech stack. FastAPI, SQLAlchemy +SQLite

```bash
url-shortener/
├── app/
│   ├── __init__.py
│   ├── database.py   # engine, session, Base
│   ├── models.py     # the URL table
│   ├── schemas.py    # request/response shapes
│   ├── utils.py      # short-code generator
│   └── main.py       # the API endpoints
├── tests/
│   └── test_main.py
└── requirements.txt
```

1. Create the virtual environment (only once)
   
```bash
python -m venv .venv
```

3. Allow activation scripts (only once per Windows user, if activation is blocked)
   
```bash 
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

5. Activate it
   
```bash
.\.venv\Scripts\Activate.ps1
```

7. Install dependencies

```bash
    python -m pip install --upgrade pip
    pip install -r requirements.txt 
```

5. Run the tests

```bash
python -m pytest -v
```

6. Start the server, then open http://localhost:8000/docs

```bash
uvicorn app.main:app --reload
```
