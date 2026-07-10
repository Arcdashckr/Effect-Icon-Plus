@echo off
chcp 65001 > nul
title Effect-Icon-Plus Araç Kiti

:menu
cls
echo ==================================================
echo         EFFECT-ICON-PLUS OTOMASYON MENÜSÜ
==================================================
echo.
echo [1] Modrinth Koleksiyonundan Modları İndir (Download)
echo [2] Modlardan İkonları Ayıkla ve Büyüt (Extract ve Scale)
echo [3] Renk Paletine Göre Çerçevele ve Birleştir (Merge)
echo [4] Önizleme Gridi Oluştur (Display Grid)
echo [5] Çıkış
echo.
echo ==================================================
set /p secim="Lütfen yapmak istediğiniz işlemi seçin (1-5): "

if "%secim%"=="1" goto download
if "%secim%"=="2" goto extract
if "%secim%"=="3" goto merge
if "%secim%"=="4" goto grid
if "%secim%"=="5" goto exit
goto menu

:download
cls
echo 🚀 Koleksiyon İndirme Başlatılıyor...
echo.
python collection_downloader.py
echo.
pause
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