def test_imports():
    modules = [
        'fastapi', 'uvicorn', 'pydantic',
        'sklearn', 'pandas', 'numpy', 'joblib'
    ]
    
    print("Testing module imports...")
    all_ok = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            all_ok = False
    
    if all_ok:
        print("\n🎉 All modules imported successfully!")
        return True
    else:
        print("\n⚠️ Some modules are missing. Please install them.")
        return False

if __name__ == "__main__":
    test_imports()