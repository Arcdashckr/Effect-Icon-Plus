@echo off

title EFFECT-ICON-PLUS TOOLKIT

:menu
cls
echo ==================================================
echo         EFFECT-ICON-PLUS TOOLKIT
echo ==================================================
echo.
echo [1] Download Mod or Collection
echo [2] Extract and Scale Effect Icons
echo [3] Merge Frames
echo [4] Create Display Grid
echo [5] Manage Mod Metadata
echo [6] Generate Repository Files
echo [7] Run Full Pipeline
echo [8] Clean Temporary Files
echo [9] Exit
echo.
echo ==================================================
set /p choice="Please select an option (1-9): "

if "%choice%"=="1" goto download
if "%choice%"=="2" goto extract
if "%choice%"=="3" goto merge
if "%choice%"=="4" goto grid
if "%choice%"=="5" goto metadata
if "%choice%"=="6" goto repo_files
if "%choice%"=="7" goto pipeline
if "%choice%"=="8" goto clean
if "%choice%"=="9" goto exit
goto menu

:download
cls
echo Starting Mod or Collection Downloader...
echo.
python collection_downloader.py
echo.
pause
goto menu

:extract
cls
echo Starting Icon Extractor and Scaler...
echo.
python extract_and_scale.py
echo.
pause
goto menu

:merge
cls
echo Starting Frame Colorizing and Merging...
echo.
python merge_frames.py
echo.
pause
goto menu

:grid
cls
echo Starting Preview Grid Creator...
echo.
python create_display.py
echo.
pause
goto menu

:metadata
cls
echo Starting Metadata Manager...
echo.
python metadata_manager.py
echo.
pause
goto menu

:repo_files
cls
echo Generating Repository Files (stats.json, compatibility.md)...
echo.
python generate_repo_files.py
echo.
pause
goto menu

:pipeline
cls
echo Starting Full Pipeline...
echo.
echo === Step 1: Download Mod or Collection ===
python collection_downloader.py
echo.
echo === Step 2: Extract and Scale Icons ===
python extract_and_scale.py
echo.
echo === Step 3: Colorize and Merge Frames ===
python merge_frames.py
echo.
echo === Step 4: Create Preview Grid ===
python create_display.py
echo.
echo === Step 5: Update Repository Files ===
python generate_repo_files.py
echo.
echo Full pipeline completed successfully!
pause
goto menu

:clean
cls
echo Cleaning Temporary Files...
echo.
python clean_temp.py
echo.
pause
goto menu

:exit
exit