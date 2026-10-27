import os
import sqlite3
from contextlib import closing
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

DB = os.getenv('DATABASE_PATH', 'helpdesk.db')
app = FastAPI(title='HelpDesk AI Starter')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173'], allow_methods=['*'], allow_headers=['*'])

class Ticket(BaseModel):
    title: str
    description: str

class Question(BaseModel):
    question: str

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event('startup')
def init():
    with closing(connect()) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT NOT NULL, status TEXT NOT NULL DEFAULT "open")')
        conn.commit()

@app.get('/tickets')
def list_tickets():
    with closing(connect()) as conn:
        return [dict(row) for row in conn.execute('SELECT * FROM tickets ORDER BY id DESC')]

@app.post('/tickets')
def create_ticket(ticket: Ticket):
    with closing(connect()) as conn:
        cursor = conn.execute('INSERT INTO tickets(title, description) VALUES (?, ?)', (ticket.title, ticket.description))
        conn.commit()
        return {'id': cursor.lastrowid, **ticket.model_dump(), 'status': 'open'}

@app.post('/assistant')
def assistant(question: Question):
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        return {'answer': 'AI is not configured yet. Add OPENAI_API_KEY in your local environment to enable it.', 'configured': False}
    from openai import OpenAI
    client = OpenAI(api_key=key)
    response = client.responses.create(model=os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'), instructions='You are a helpful support assistant. Do not claim to have accessed tickets or documents unless provided.', input=question.question)
    return {'answer': response.output_text, 'configured': True}
