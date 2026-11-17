@echo off
setlocal enabledelayedexpansion
title Tales of Destiny DC - Atualizacao rapida
cd /d "%~dp0"
set "RAIZ=%~dp0"
set "JOGO=%RAIZ%JOGO"
set "TODT=%RAIZ%ferramentas\historia\ToDDCTools_v1.1.exe"
set "LOG=%RAIZ%log_rapido.txt"
echo Log da atualizacao rapida > "%LOG%"
echo ============================================================
echo  Atualizacao rapida: so copia os arquivos prontos e remonta
echo  (use depois de ja ter rodado o APLICAR_TRADUCAO.bat uma vez)
echo ============================================================
if not exist "%JOGO%\DAT_FILES" (
    echo ERRO: rode primeiro o APLICAR_TRADUCAO.bat completo uma vez.
    goto :fim
)
echo Copiando arquivos prontos...
for %%F in ("%RAIZ%textos\prontos\*.*") do copy /y "%%F" "%JOGO%\DAT_FILES\" >nul
echo Remontando o DAT.BIN... ^(NAO feche a janela^)
pushd "%JOGO%"
if exist new_DAT.BIN del new_DAT.BIN
if exist new_DAT.TBL del new_DAT.TBL
"%TODT%" pack DAT.BIN DAT.TBL >> "%LOG%" 2>&1
popd
if not exist "%RAIZ%SAIDA" mkdir "%RAIZ%SAIDA"
if exist "%JOGO%\new_DAT.BIN" (
    move /y "%JOGO%\new_DAT.BIN" "%RAIZ%SAIDA\DAT.BIN" >nul
    move /y "%JOGO%\new_DAT.TBL" "%RAIZ%SAIDA\DAT.TBL" >nul
    echo.
    echo PRONTO! Pegue SAIDA\DAT.BIN e SAIDA\DAT.TBL
    echo ^(e o textos\SLPS\SLPS_258.42 se ele tiver mudado^)
) else (
    echo ERRO: o DAT.BIN novo nao foi gerado. Mande o log_rapido.txt
)
:fim
echo.
pause
