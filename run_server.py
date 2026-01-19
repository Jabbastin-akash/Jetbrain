"""Run the VALORANT Scouting Assistant Server"""
import uvicorn
import sys

if __name__ == "__main__":
    print("=" * 60)
    print("  VALORANT MATCHUP SCOUTING ASSISTANT")
    print("  Category 2 - Automated Scouting Report Generator")
    print("=" * 60)
    print("")
    print("Server starting at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("")
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    print("")

    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
