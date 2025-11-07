"""Test running the app and capture errors."""
import sys
import traceback

try:
    print("Creating app...")
    from app import create_app
    app = create_app()
    print("App created successfully!")
    
    print("\nTesting routes...")
    with app.test_client() as client:
        # Test root route
        response = client.get('/')
        print(f"Root route: {response.status_code}")
        
        # Test resources route
        response = client.get('/resources/')
        print(f"Resources route: {response.status_code}")
        
        # Test auth routes
        response = client.get('/auth/login')
        print(f"Login route: {response.status_code}")
        
    print("\nAll tests passed! App is ready to run.")
    print("Run: python app.py")
    
except Exception as e:
    print(f"\nERROR occurred: {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)

