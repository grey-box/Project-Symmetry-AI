#!/bin/bash

# Project Symmetry AI - Complete Application Restart Script
# This script kills all existing components, rebuilds the app, and relaunches it
# Based on the installation guide in INSTALLATION.md

set -e  # Exit on any error

echo "🔄 Project Symmetry AI - Complete Application Restart"
echo "===================================================="

# Function to kill processes on different ports
kill_processes() {
    echo "🔪 Killing existing processes..."
    
    # Log existing node/npm processes before killing
    echo "  🔍 Existing node/npm processes before cleanup:"
    ps aux | grep -E "(node|npm)" | grep -v grep || echo "    No node/npm processes found"
    echo ""
    
    # Kill processes on port 8000 (backend)
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
        echo "  ⚠️  Killing backend server on port 8000..."
        pkill -f "python.*main.py" || true
        pkill -f "uvicorn.*app.main" || true
        sleep 2
    fi
    
    # Kill processes on port 5173 (frontend dev server)
    if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
        echo "  ⚠️  Killing frontend dev server on port 5173..."
        pkill -f "vite" || true
        pkill -f "npm.*start" || true
        sleep 2
    fi
    
    # Kill any remaining npm/node processes - BUT BE MORE SPECIFIC
    echo "  ⚠️  Cleaning up project-specific node processes..."
    
    # Only kill node/npm processes that are related to this project
    # by looking for processes in the current directory tree
    echo "    Targeting processes in current project directory..."
    
    # Kill node processes that are in this project directory
    pkill -f "node.*$(pwd)" || true
    pkill -f "npm.*$(pwd)" || true
    
    # Also kill common frontend build tools if they're in our project
    pkill -f "vite.*$(pwd)" || true
    pkill -f "webpack.*$(pwd)" || true
    
    echo "  ✅ Project-specific processes killed"
    
    # Log remaining node/npm processes after cleanup
    echo "  🔍 Remaining node/npm processes after cleanup:"
    ps aux | grep -E "(node|npm)" | grep -v grep || echo "    No node/npm processes found"
    echo ""
}

# Function to setup Python environment
setup_python_env() {
    echo "🐍 Setting up Python environment..."
    
    cd backend-fastapi
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "  📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo "  🔄 Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    echo "  📦 Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Install PyInstaller if not already installed
    if ! pip show pyinstaller >/dev/null 2>&1; then
        echo "  📦 Installing PyInstaller..."
        pip install pyinstaller
    fi
    
    echo "  ✅ Python environment setup complete"
}

# Function to build Python executable
build_python_executable() {
    echo "🔨 Building Python executable..."
    
    cd app
    
    # Build with PyInstaller
    pyinstaller -F main.py
    
    echo "  ✅ Python executable built"
}

# Function to setup frontend
setup_frontend() {
    echo "🌐 Setting up frontend..."
    
    cd ../../ui
    
    # Install dependencies
    echo "  📦 Installing Node.js dependencies..."
    npm install
    
    echo "  ✅ Frontend setup complete"
}

# Function to start the application
start_application() {
    echo "🚀 Starting application..."
    
    # Start backend in background
    echo "  🔧 Starting backend server..."
    cd ../backend-fastapi/app
    # Create a temporary script with proper PYTHONPATH and virtual environment activation
    cat > temp_backend_run.sh << 'EOF'
#!/bin/bash
cd /Users/francois/IdeaProjects/Project-Symmetry-AI/backend-fastapi/app
source ../venv/bin/activate
export PYTHONPATH="/Users/francois/IdeaProjects/Project-Symmetry-AI/backend-fastapi:$PYTHONPATH"
python main.py
EOF
    chmod +x temp_backend_run.sh
    # Use absolute path to ensure the script is executed correctly
    nohup /Users/francois/IdeaProjects/Project-Symmetry-AI/backend-fastapi/app/temp_backend_run.sh > /Users/francois/IdeaProjects/Project-Symmetry-AI/backend-fastapi/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "  ✅ Backend started (PID: $BACKEND_PID)"
    
    # Wait for backend to start
    echo "  ⏳ Waiting for backend to start..."
    sleep 5
    
    # Start frontend
    echo "  🌐 Starting frontend server..."
    cd ../../ui
    nohup npm run start > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "  ✅ Frontend started (PID: $FRONTEND_PID)"
    
    # Display status
    echo ""
    echo "🎉 Application started successfully!"
    echo "==================================="
    echo "📊 Backend:  http://localhost:8000"
    echo "📊 Frontend: http://localhost:5173"
    echo "📊 Logs:"
    echo "   - Backend: backend.log"
    echo "   - Frontend: frontend.log"
    echo ""
    echo "🔧 To stop the application:"
    echo "   pkill -f 'python.*main.py'"
    echo "   pkill -f 'npm.*start.*$(pwd)'"
    echo "   pkill -f 'vite.*$(pwd)'"
    echo ""
    echo "   💡 For safer process management, use:"
    echo "   pkill -f 'python.*main.py'  # Backend only"
    echo "   pkill -f 'npm.*start.*Project-Symmetry-AI'  # Frontend only"
    echo ""
    echo "📋 Process IDs:"
    echo "   - Backend: $BACKEND_PID"
    echo "   - Frontend: $FRONTEND_PID"
}

# Main execution
main() {
    echo "🗓️  $(date)"
    echo ""
    
    # Step 1: Kill existing processes
    kill_processes
    
    # Step 2: Setup Python environment
    setup_python_env
    
    # Step 3: Build Python executable
    echo "  🔨 Building Python executable..."
    build_python_executable
    
    # Step 4: Setup frontend
    setup_frontend
    
    # Step 5: Start application
    start_application
}

# Run main function
main