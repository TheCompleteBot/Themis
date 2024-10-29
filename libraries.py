# libraries.py
import os
import json
import logging
from typing import List, Dict, Optional, Union
from datetime import datetime
import re
from dotenv import load_dotenv
from openai import OpenAI  # Updated import

# Load environment variables
load_dotenv()

# Configure OpenAI API key
os.environ['OPENAI_API_KEY'] = 'your-api-key-here'  # Replace with your actual API key
# Or better, add it to a .env file and load it:
# OPENAI_API_KEY=your-api-key-here

__all__ = [
    'os', 'json', 'logging', 'List', 'Dict', 'Optional', 
    'Union', 'datetime', 're', 'OpenAI'
]