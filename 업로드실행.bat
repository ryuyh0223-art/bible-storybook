@echo off
echo ===================================================
echo [Happy Pang] Auto Upload Script
echo ===================================================
echo.
echo 1. Copying images...
mkdir "bible-storybook-special-promise\assets\images" 2>nul
xcopy "C:\Users\P1\Downloads\0510 해피팡 코딩용\*" "bible-storybook-special-promise\assets\images" /E /I /Y /Q
echo Image copy completed!
echo.
echo 2. Uploading to GitHub... (Please wait)
git add .
git commit -m "Add new storybook: God's Special Promise"
git push
echo.
echo ===================================================
echo Upload successfully completed!
echo Please check the GitHub URL.
echo Press any key to close this window...
pause >nul
