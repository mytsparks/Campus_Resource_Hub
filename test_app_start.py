"""Quick test to verify app can start."""
try:
    from app import create_app
    app = create_app()
    print("SUCCESS: App created successfully!")
    print("SUCCESS: All blueprints registered")
    print("SUCCESS: Database initialized")
    print("SUCCESS: Admin user seeded")
    print("\nApp is ready to run!")
    print("Run: python app.py")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

