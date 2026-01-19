"""Test script to verify imports and configuration."""
import sys
print("Python version:", sys.version)

try:
    print("Testing imports...")
    from fastapi import FastAPI
    print("[OK] FastAPI")

    from pydantic import BaseModel
    print("[OK] Pydantic")

    import httpx
    print("[OK] httpx")

    import google.generativeai as genai
    print("[OK] Gemini")

    from cachetools import TTLCache
    print("[OK] cachetools")

    from jinja2 import Environment
    print("[OK] Jinja2")

    print("\n--- Testing application modules ---")

    from config import get_settings
    settings = get_settings()
    print("[OK] Config loaded")
    print(f"  GRID Key: {settings.grid_api_key[:15]}..." if settings.grid_api_key else "  GRID Key: Not set")
    print(f"  Gemini Key: {settings.gemini_api_key[:15]}..." if settings.gemini_api_key else "  Gemini Key: Not set")

    from grid_client.models import Team, Match
    print("[OK] Grid models")

    from grid_client.client import GridClient
    print("[OK] Grid client")

    from analysis.stats import StatsCalculator
    print("[OK] Stats calculator")

    from analysis.patterns import PatternDetector
    print("[OK] Pattern detector")

    from analysis.report_builder import ScoutingReportBuilder
    print("[OK] Report builder")

    from ai.prompts import PromptTemplates
    print("[OK] AI prompts")

    from ai.gemini_client import GeminiClient
    print("[OK] Gemini client")

    print("\n=== All imports successful! ===")
    print("\nReady to start the application!")

except Exception as e:
    print(f"\n[ERROR]: {e}")
    import traceback
    traceback.print_exc()
