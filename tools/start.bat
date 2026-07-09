@echo off
chcp 65001 > nul
title Effect-Icon-Plus Araç Kiti

:menu
cls
echo ==================================================
echo         EFFECT-ICON-PLUS OTOMASYON MENÜSÜ
echo ==================================================
echo.
echo [1] Modlardan İkonları Ayıkla ve Büyüt (Extract ve Scale)
echo [2] Renk Paletine Göre Çerçevele ve Birleştir (Merge)
echo [3] Önizleme Gridi Oluştur (Display Grid)
echo [4] Çıkış
echo.
echo ==================================================
set /p secim="Lütfen yapmak istediğiniz işlemi seçin (1-4): "

if "%secim%"=="1" goto extract
if "%secim%"=="2" goto merge
if "%secim%"=="3" goto grid
if "%secim%"=="4" goto exit
goto menu

:extract
cls
echo 🚀 İkon Ayıklama Başlatılıyor...
echo.
python extract_and_scale.py
echo.
pause
goto menu

:merge
cls
echo 🎨 Renklendirme ve Birleştirme Başlatılıyor...
echo.
python merge_frames.py
echo.
pause
goto menu

:grid
cls
echo 🖼️ Önizleme Gridi Oluşturma Başlatılıyor...
echo.
python create_display.py
echo.
pause
goto menu

:exit
exit