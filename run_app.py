"""Run the Flask app with better error handling."""
import sys
import traceback

if __name__ == '__main__':
    try:
        from app import create_app
        print("Starting Campus Resource Hub...")
        app = create_app()
        print("App initialized successfully!")
        print("Starting server on http://127.0.0.1:5000")
        print("Press CTRL+C to stop the server")
        app.run(debug=True, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: Failed to start application")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)

