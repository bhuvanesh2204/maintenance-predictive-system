import subprocess
import sys
import os

def run_command(command):
    """Run a command and return whether it was successful"""
    try:
        print(f"Running: {command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Installing Predictive Maintenance Agent Dependencies...")
    
    # List of packages to install
    packages = [
        "setuptools",
        "wheel",
        "numpy",
        "pandas", 
        "scikit-learn",
        "joblib",
        "fastapi",
        "uvicorn",
        "pydantic",
        "python-multipart"
    ]
    
    # Install each package
    success_count = 0
    for package in packages:
        if run_command(f'"{sys.executable}" -m pip install {package}'):
            success_count += 1
    
    print(f"\n📊 Installation Summary: {success_count}/{len(packages)} packages installed successfully")
    
    if success_count == len(packages):
        print("✅ All dependencies installed successfully!")
        
        # Try to generate the model
        print("\n🤖 Generating AI model...")
        try:
            from model import generate_sample_data, train_model
            generate_sample_data("sensor_data.csv", 1000)
            train_model("sensor_data.csv", "model.pkl")
            print("✅ Model generated successfully!")
        except Exception as e:
            print(f"❌ Model generation failed: {e}")
            
        # Start the application
        print("\n🌐 Starting the web application...")
        os.system(f'"{sys.executable}" app.py')
    else:
        print("❌ Some packages failed to install. Please check the errors above.")

if __name__ == "__main__":
    main()