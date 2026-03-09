"""
MODULE: gemini_tools.py
PURPOSE: Reusable AI Architect interface for the O'Reilly Prompt Engineering Masterclass.
FEATURES:
    - Auto-loads credentials via .env using Absolute Path Discovery.
    - Supports System Instructions for role-playing (Firmware-level prompting).
    - Tracks Usage Metadata (In/Out Tokens) via response.usage_metadata.
    - Estimates Costs based on 2026 Flash-Lite rates ($0.075/$0.30 per 1M).
    - PERSISTENCE: SQLite Database integration for "Inception-to-Date" tracking.
    - Appends all interactions to 'masterclass_log.txt' for persistent auditing.
    - Designed for Python 3.14.0 environments.
"""

import os
import sqlite3
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Pricing constants for Gemini 3.1 Flash-Lite (March 2026)
COST_PER_1M_INPUT = 0.075
COST_PER_1M_OUTPUT = 0.30

# --- ABSOLUTE PATH CALIBRATION ---
# This finds the 'PromptMasterclass' root folder by looking two levels up from this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'gemini_history.db')
LOG_PATH = os.path.join(BASE_DIR, 'data', 'masterclass_log.txt')
ENV_PATH = os.path.join(BASE_DIR, 'root', '.env')

def init_db():
    """Initializes the SQLite database in the data folder."""
    # Ensure data folder exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            prompt TEXT,
            model TEXT,
            in_tokens INTEGER,
            out_tokens INTEGER,
            cost REAL
        )
    ''')
    conn.commit()
    conn.close()

def get_lifetime_totals():
    """Calculates cumulative totals from the database since inception."""
    if not os.path.exists(DB_PATH):
        return (0, 0, 0.0)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(in_tokens), SUM(out_tokens), SUM(cost) FROM logs')
    totals = cursor.fetchone()
    conn.close()
    return (totals[0] or 0, totals[1] or 0, totals[2] or 0.0)

def ask_architect(prompt, model_id="gemini-3.1-flash-lite-preview", system_instr=None):
    """
    Modular function to communicate with Gemini and log session data.
    Returns: (text, cost, server_model, in_tokens, out_tokens, lifetime_tuple)
    """
    # Load the .env using the absolute path we calculated
    load_dotenv(dotenv_path=ENV_PATH)

    # Check if key exists in environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return f"CRITICAL ERROR: API Key not found at {ENV_PATH}", 0.0, "KEY_ERROR", 0, 0, (0,0,0.0)

    client = genai.Client(api_key=api_key)
    init_db()

    if not system_instr:
        system_instr = "You are a Senior AI Architect helping an engineer."

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system_instr)
        )

        usage = response.usage_metadata
        in_tokens = usage.prompt_token_count
        out_tokens = usage.candidates_token_count
        actual_model = getattr(response, 'model_id', model_id)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        total_req_cost = ((in_tokens * COST_PER_1M_INPUT) + (out_tokens * COST_PER_1M_OUTPUT)) / 1000000

        # SQLite Database Persistence
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (timestamp, prompt, model, in_tokens, out_tokens, cost)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, prompt, actual_model, in_tokens, out_tokens, total_req_cost))
        conn.commit()
        conn.close()

        # Traditional Redundant File Logging
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"TIMESTAMP: {timestamp} | MODEL: {actual_model} | COST: ${total_req_cost:.6f}\n")

        life_in, life_out, life_cost = get_lifetime_totals()
        return response.text, total_req_cost, actual_model, in_tokens, out_tokens, (life_in, life_out, life_cost)

    except Exception as e:
        return f"Circuit Break (Error): {str(e)}", 0.0, "ERROR_STATE", 0, 0, (0, 0, 0.0)