@echo off
echo 🚀 Starting VFS Visa Bot System
echo ================================

echo.
echo 📦 Building and starting Docker containers...
docker-compose down
docker-compose up --build -d

echo.
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak > nul

echo.
echo 🧪 Running system tests...
python test_system.py

echo.
echo ✅ System started!
echo.
echo 🌐 Dashboard: http://localhost:3000
echo 🔧 API Docs: http://localhost:8000/docs
echo.
echo 📋 To view logs:
echo    docker-compose logs -f
echo.
echo 🛑 To stop system:
echo    docker-compose down
echo.
pause
