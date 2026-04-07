@echo off
REM GitHub Upload Script for Travel Itinerary Planner (Windows)
REM ============================================================

echo.
echo ==========================================
echo TRAVEL ITINERARY PLANNER
echo GitHub Upload Process
echo ==========================================
echo.

REM Step 1: Initialize Git Repository
echo [1/6] Initializing Git Repository...
git init
echo ✓ Git initialized
echo.

REM Step 2: Add all files
echo [2/6] Adding all files to Git tracking...
git add .
echo ✓ All files added
echo.

REM Step 3: Create initial commit
echo [3/6] Creating initial commit...
git commit -m "Initial commit: Travel Itinerary Planner OpenEnv environment"
echo ✓ Commit created
echo.

REM Step 4: Display setup instructions
echo [4/6] Setup Instructions - GO TO GITHUB:
echo ==========================================
echo.
echo 1. Go to https://github.com and sign in
echo 2. Click "New repository" (green button)
echo 3. Repository name: travel-itinerary-planner
echo 4. Make it PUBLIC
echo 5. DO NOT check any boxes
echo 6. Click "Create repository"
echo.
echo ==========================================
echo.

REM Step 5: Instructions for connecting to GitHub
echo [5/6] AFTER creating repository on GitHub:
echo ==========================================
echo.
echo Replace YOUR_USERNAME with your actual GitHub username:
echo.
echo git remote add origin https://github.com/YOUR_USERNAME/travel-itinerary-planner.git
echo git push -u origin main
echo.
echo ==========================================
echo.

REM Step 6: Verification commands
echo [6/6] Verify everything worked:
echo ==========================================
echo.
echo Run these commands:
echo   git remote -v
echo   git status
echo.
echo Then visit: https://github.com/YOUR_USERNAME/travel-itinerary-planner
echo.
echo ==========================================
echo.
pause
