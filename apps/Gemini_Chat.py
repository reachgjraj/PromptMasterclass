"""
PROJECT: Gemini Chat UI - Prompt Engineering Sandbox
PURPOSE: Interactive terminal interface for Prompt Engineering practice.
INSTRUCTION MANUAL SUMMARY:
    - Persona-Based: Change ARCHITECTURE_PERSONA to update the AI's expert role.
    - Session-Aware: Tracks cumulative costs AND running token totals (In/Out).
    - Database-Integrated: Tracks "Overall Consumed Since Inception" via SQLite.
    - Safe-Exit: Prints final financial and token usage metrics upon termination.
    - Modular: Imports core logic from gemini_tools.py to keep UI code clean.
"""

from core.gemini_tools import ask_architect
from datetime import datetime

# --- Configuration Area ---
ARCHITECTURE_PERSONA = """
You are a Senior AI Architect helping an Electrical Engineer master Prompt Engineering.
Focus on Python 3.14 best practices, software testing, and engineering logic.
Explain complex concepts using analogies to circuits, signals, and systems.
"""

MODEL_TO_USE = "gemini-3.1-flash-lite-preview"
# ---------------------------

def run_chat():
    session_total_cost = 0.0
    session_total_in = 0
    session_total_out = 0

    print(f"--- Gemini Architect Session Started: {datetime.now().strftime('%H:%M')} ---")
    print(f"Targeting: {MODEL_TO_USE}")
    print("Commands: 'exit' to quit | 'clear' to reset terminal view\n")

    while True:
        user_q = input("User > ")

        if user_q.lower() in ['exit', 'quit', 'bye']:
            print("\n" + "="*50)
            print("SESSION TERMINATED - FINAL TOTALS")
            print(f"Cumulative Cost:   ${session_total_cost:.6f}")
            print(f"Total Tokens In:  {session_total_in}")
            print(f"Total Tokens Out: {session_total_out}")
            print("="*50)
            break

        if user_q.lower() == 'clear':
            print("\n" * 50)
            continue

        answer, cost, server_model, in_t, out_t, lifetime = ask_architect(
            prompt=user_q,
            model_id=MODEL_TO_USE,
            system_instr=ARCHITECTURE_PERSONA
        )

        session_total_cost += cost
        session_total_in += in_t
        session_total_out += out_t

        print(f"\nArchitect ({server_model}): {answer}")
        print(f"[CURRENT] In Token: {in_t} | Out Token: {out_t} | Cost: ${cost:.6f}")
        print(f"[SESSION Total] In Token: {session_total_in} | Out Token: {session_total_out} | Cost: ${session_total_cost:.6f}")
        print(f"[OVERALL Lifetime] In Token: {lifetime[0]} | Out Token: {lifetime[1]} | Cost: ${lifetime[2]:.6f}\n")

if __name__ == "__main__":
    try:
        run_chat()
    except Exception as e:
        print(f"\nFATAL SYSTEM ERROR: {e}")
    except KeyboardInterrupt:
        print("\nSession interrupted by hardware interrupt.")

    input("\nExecution finished. Press Enter to close this window...")