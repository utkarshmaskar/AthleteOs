import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
# `llama3-70b-8192` is decommissioned on Groq.
# Use env override when needed: MODEL_NAME=...
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
