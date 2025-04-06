#!/usr/bin/env python3
"""
Test script to verify our refactored module imports are working correctly.
Just run this script to check if imports work as expected.
"""

import sys
import os

# Make sure we can find the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

# Test utils imports
print("Importing from utils.sugar_utils...")
from utils.sugar_utils import (
    match_list_comprehension, match_set_comprehension, match_dict_comprehension,
    match_enumerate_pattern, match_ternary_operator, handle_code_errors,
    create_list_comprehension, create_set_comprehension
)
print("✓ Successfully imported utils.sugar_utils")

# Test importing major modules
try:
    print("Importing from agents.parser_agent...")
    from agents.parser_agent import ParserAgent
    print("✓ Successfully imported agents.parser_agent")
except ImportError as e:
    print(f"✗ Error importing ParserAgent: {e}")

try:
    print("Importing from transformers.sugar_transformer...")
    from transformers.sugar_transformer import transform_code, SugarTransformer
    print("✓ Successfully imported transformers.sugar_transformer")
except ImportError as e:
    print(f"✗ Error importing SugarTransformer: {e}")

try:
    print("Importing from rules.sugaring_rules...")
    from rules.sugaring_rules import SUGARING_RULEBOOK
    print("✓ Successfully imported rules.sugaring_rules")
except ImportError as e:
    print(f"✗ Error importing SUGARING_RULEBOOK: {e}")

print("\nAll import tests completed.")
print("Note: Some imports may fail if external dependencies like 'crewai' aren't installed.") 