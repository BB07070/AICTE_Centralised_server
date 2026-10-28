import os, sys, subprocess

os.environ["SERVER"] = "http://localhost:8000" # Change to Ngrok URL if remote
os.environ["SESSION_FILE"] = ".session_pgrc"

subprocess.run([sys.executable, "client.py"])