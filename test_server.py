#!/usr/bin/env python3
"""
Simple server test to diagnose issues
"""

import os
import sys
import socket

def test_basic_flask():
    """Test if basic Flask works"""
    try:
        from flask import Flask
        
        app = Flask(__name__)
        
        @app.route('/')
        def hello():
            return '<h1>Hello! Academia Validator Test Server</h1><p>If you can see this, Flask is working!</p>'
        
        @app.route('/test')
        def test():
            return {'status': 'working', 'message': 'API endpoint test successful'}
        
        print("✅ Basic Flask test successful")
        return app
    except Exception as e:
        print(f"❌ Basic Flask test failed: {e}")
        return None

def check_port(port=5000):
    """Check if port is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"⚠️  Port {port} is already in use")
            return False
        else:
            print(f"✅ Port {port} is available")
            return True
    except Exception as e:
        print(f"❌ Error checking port {port}: {e}")
        return False

def main():
    print("=== Academia Validator Server Test ===")
    print("Diagnosing server issues...\n")
    
    # Check port availability
    print("1. Checking port availability...")
    port_available = check_port(5000)
    
    if not port_available:
        print("Trying alternative port 5001...")
        port_available = check_port(5001)
        port = 5001
    else:
        port = 5000
    
    # Test basic Flask
    print("\n2. Testing basic Flask functionality...")
    app = test_basic_flask()
    
    if app is None:
        print("Cannot proceed - Flask is not working")
        return False
    
    # Try to start server
    print(f"\n3. Starting test server on port {port}...")
    try:
        print(f"🚀 Test server starting...")
        print(f"📍 Visit: http://127.0.0.1:{port}")
        print(f"📍 Or: http://localhost:{port}")
        print(f"📍 Test API: http://localhost:{port}/test")
        print("\nPress Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start the server
        app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        print("\nTrying to diagnose the issue...")
        
        # Check if it's a permission issue
        if "Permission denied" in str(e):
            print("This might be a permission issue. Try:")
            print("1. Run as administrator")
            print("2. Use a different port (like 8080)")
        
        # Check if it's a firewall issue
        elif "Address already in use" in str(e):
            print("Port is already in use. Try:")
            print("1. Close other applications using this port")
            print("2. Use a different port")
            
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)