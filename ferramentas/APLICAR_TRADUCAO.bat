@echo off
setlocal enabledelayedexpansion
title Tales of Destiny DC - Traducao PT-BR (teste)
cd /d "%~dp0"
set "RAIZ=%~dp0"
set "JOGO=%RAIZ%JOGO"
set "DAT=%RAIZ%JOGO\DAT"
set "ORIG=%RAIZ%originais"
set "TODT=%RAIZ%ferramentas\historia\ToDDCTools_v1.1.exe"
set "SCE=%RAIZ%ferramentas\scework\sceWork.exe"
set "PAKC=%RAIZ%ferramentas\skits"
set "LOG=%RAIZ%log.txt"
set ERROS=0
echo Log da traducao > "%LOG%"

echo ============================================================
echo  Tales of Destiny Director's Cut - Traducao PT-BR (teste)
echo ============================================================
echo.

if not exist "%JOGO%\DAT.BIN" goto :faltando
if not exist "%JOGO%\DAT.TBL" goto :faltando
if not exist "%ORIG%" mkdir "%ORIG%"

rem ---------------------------------------------------------------
rem 1) Desmontar o DAT.BIN (so na primeira vez)
rem ---------------------------------------------------------------
if exist "%DAT%\MGLK" (
    echo [1/4] DAT.BIN ja foi desmontado antes. Pulando.
) else (
    echo [1/4] Desmontando o DAT.BIN... ^(pode levar alguns minutos^)
    pushd "%JOGO%"
    "%TODT%" unpack DAT.BIN DAT.TBL >> "%LOG%" 2>&1
    popd
    if not exist "%DAT%\MGLK" (
        echo ERRO: nao consegui desmontar o DAT.BIN. Veja o log.txt
        goto :fim
    )
)
if exist "%JOGO%\DAT_FILES" rmdir /s /q "%JOGO%\DAT_FILES"
mkdir "%JOGO%\DAT_FILES"

rem ---------------------------------------------------------------
rem 2) Cenas da historia (RSCE dentro de MGLK)
rem    Sempre parte do MGLK original guardado em "originais".
rem ---------------------------------------------------------------
echo.
echo [2/4] Colocando o texto das cenas da historia...
for %%T in ("%RAIZ%textos\historia\*.txt") do (
    set "NOME=%%~nT"
    for /f "tokens=1 delims=_" %%A in ("%%~nT") do set "NUM=%%A"
    set "MGLK=%DAT%\MGLK\!NUM!.mglk"
    if not exist "%ORIG%\!NUM!.mglk" if exist "!MGLK!" copy /y "!MGLK!" "%ORIG%\" >nul
    if not exist "%ORIG%\!NUM!.mglk" (
        echo    ERRO: nao achei !NUM!.mglk
        set /a ERROS+=1
    ) else (
        copy /y "%ORIG%\!NUM!.mglk" "!MGLK!" >nul
        if exist "%DAT%\MGLK\!NUM!" rmdir /s /q "%DAT%\MGLK\!NUM!"
        pushd "%DAT%\MGLK"
        "%TODT%" unmglk !NUM!.mglk >> "%LOG%" 2>&1
        popd
        set "RSCE="
        if exist "%DAT%\MGLK\!NUM!" (
            pushd "%DAT%\MGLK\!NUM!"
            for /r %%R in (*.rsce) do if /i "%%~nR"=="!NOME!" set "RSCE=%%R"
            popd
        )
        if not defined RSCE (
            echo    ERRO: nao achei !NOME!.rsce dentro de !NUM!.mglk
            set /a ERROS+=1
        ) else (
            if not exist "%ORIG%\!NOME!.rsce" copy /y "!RSCE!" "%ORIG%\" >nul
            for %%R in ("!RSCE!") do copy /y "%%T" "%%~dpR!NOME!.txt" >nul
            set "FALHOU="
            if exist "%RAIZ%textos\rsce\!NOME!.rsce" (
                rem Arquivo ja montado e testado: so copia por cima
                copy /y "%RAIZ%textos\rsce\!NOME!.rsce" "!RSCE!" >nul
                if errorlevel 1 set "FALHOU=1"
                echo Usando arquivo pronto: !NOME!.rsce >> "%LOG%"
            ) else (
                "%SCE%" -r "!RSCE!" < nul > "%RAIZ%saida.log" 2>&1
                if errorlevel 1 set "FALHOU=1"
                findstr /i /c:"Exception" /c:"FATAL" /c:"Different amount" /c:"Couldn't insert" "%RAIZ%saida.log" >nul && set "FALHOU=1"
                type "%RAIZ%saida.log" >> "%LOG%"
            )
            if defined FALHOU (
                echo    ERRO: o sceWork nao aceitou o texto de !NOME!. Veja o log.txt
                set /a ERROS+=1
            ) else (
                pushd "%DAT%\MGLK"
                "%TODT%" mglk !NUM!.mglk >> "%LOG%" 2>&1
                popd
                copy /y "!MGLK!" "%JOGO%\DAT_FILES\" >nul
                echo    OK: !NOME!
            )
        )
    )
)

rem ---------------------------------------------------------------
rem 3) Skits (TOD1RSCE4 dentro de PAK1/PAK3)
rem ---------------------------------------------------------------
echo.
echo [3/4] Colocando o texto das skits...
for %%T in ("%RAIZ%textos\skits\*.txt") do (
    set "NOME=%%~nT"
    for /f "tokens=1 delims=_" %%A in ("%%~nT") do set "NUM=%%A"
    rem Na ISO em ingles a skit costuma estar em PAK3 (o byte corrigido muda a deteccao)
    set "PAK="
    set "PULAR="
    for %%P in (16203 16204 16205 16206 16207 16208 16209 16210 16211 16212 16213) do if "!NUM!"=="%%P" set "PULAR=1"
    if exist "%DAT%\PAK1\!NUM!.pak1" set "PAK=%DAT%\PAK1\!NUM!.pak1" & set "EXT=pak1"
    if exist "%DAT%\PAK3\!NUM!.pak3" set "PAK=%DAT%\PAK3\!NUM!.pak3" & set "EXT=pak3"
    if defined PULAR (
        echo    Pulando !NOME! ^(fica em ingles por enquanto^)
    ) else if not defined PAK (
        echo    ERRO: nao achei !NUM!.pak1 nem !NUM!.pak3
        set /a ERROS+=1
    ) else (
        pushd "%PAKC%"
        if exist "!NUM!" rmdir /s /q "!NUM!"
        copy /y "!PAK!" "!NUM!.pak1" >nul
        pakcomposer.exe -d "!NUM!.pak1" -1 -x -u >> "%LOG%" 2>&1
        del "!NUM!.pak1" >nul 2>&1
        set "SKIT="
        if exist "!NUM!" (
            pushd "!NUM!"
            echo Arquivos dentro de !NUM!: >> "%LOG%"
            dir /b /s >> "%LOG%"
            for /r %%R in (*) do if /i "%%~nR"=="!NOME!" set "SKIT=%%R" & set "SKITEXT=%%~xR"
            popd
        )
        if not defined SKIT (
            echo    ERRO: nao achei !NOME! dentro de !NUM!.!EXT!
            set /a ERROS+=1
        ) else (
            rem O sceWork so aceita as extensoes .rsce/.tod1rsce/.tod1rsce4
            copy /y "!SKIT!" "!NOME!.tod1rsce4" >nul
            rem Os 12 bytes finais pertencem ao arquivo seguinte do pacote (a Life Bottle
            rem sobrepoe os arquivos); corta antes e devolve com -as 12, como no processo deles
            powershell -NoProfile -Command "$p='%PAKC%\!NOME!.tod1rsce4'; $b=[IO.File]::ReadAllBytes($p); [IO.File]::WriteAllBytes($p, $b[0..($b.Length-13)])"
            copy /y "%%T" "!NOME!.txt" >nul
            set "FALHOU="
            "%SCE%" -r "%PAKC%\!NOME!.tod1rsce4" -as 12 -ae < nul > "%RAIZ%saida.log" 2>&1
            if errorlevel 1 set "FALHOU=1"
            findstr /i /c:"Exception" /c:"FATAL" /c:"Different amount" /c:"Couldn't insert" "%RAIZ%saida.log" >nul && set "FALHOU=1"
            type "%RAIZ%saida.log" >> "%LOG%"
            if not defined FALHOU copy /y "!NOME!.tod1rsce4" "!SKIT!" >nul
            del "!NOME!.tod1rsce4" "!NOME!.txt" >nul 2>&1
            if defined FALHOU (
                echo    ERRO: o sceWork nao aceitou o texto de !NOME!. Veja o log.txt
                set /a ERROS+=1
            ) else (
                pakcomposer.exe -c !NUM! -1 -x -u -tod2_ps2_skit_padding >> "%LOG%" 2>&1
                if exist "!NUM!.pak1" (
                    rem Mesma correcao do modPAK1Files.py da Life Bottle: byte 0x04 de 24 para 30
                    powershell -NoProfile -Command "$p='%PAKC%\!NUM!.pak1'; $b=[IO.File]::ReadAllBytes($p); if($b[4] -eq 0x24){$b[4]=0x30; [IO.File]::WriteAllBytes($p,$b)}"
                    move /y "!NUM!.pak1" "%JOGO%\DAT_FILES\!NUM!.!EXT!" >nul
                    echo    OK: !NOME!
                ) else (
                    echo    ERRO: o pakcomposer nao gerou !NUM!.pak1. Veja o log.txt
                    set /a ERROS+=1
                )
            )
        )
        if exist "!NUM!" rmdir /s /q "!NUM!"
        popd
    )
)

rem ---------------------------------------------------------------
rem 3b) Arquivos ja prontos (titulos das skits e skits especiais)
rem ---------------------------------------------------------------
if exist "%RAIZ%textos\prontos" (
    echo.
    echo Copiando arquivos prontos...
    for %%F in ("%RAIZ%textos\prontos\*.*") do (
        copy /y "%%F" "%JOGO%\DAT_FILES\" >nul
        echo    OK: %%~nxF
    )
)

if not "%ERROS%"=="0" (
    echo.
    echo Houve %ERROS% erro^(s^). NAO vou montar o DAT.BIN. Mande o log.txt
    goto :fim
)

rem ---------------------------------------------------------------
rem 4) Remontar o DAT.BIN
rem ---------------------------------------------------------------
echo.
echo [4/4] Remontando o DAT.BIN... ^(pode levar alguns minutos, NAO feche a janela^)
pushd "%JOGO%"
if exist new_DAT.BIN del new_DAT.BIN
if exist new_DAT.TBL del new_DAT.TBL
"%TODT%" pack DAT.BIN DAT.TBL >> "%LOG%" 2>&1
popd
if exist "%JOGO%\new_DAT.BIN" (
    move /y "%JOGO%\new_DAT.BIN" "%RAIZ%SAIDA\DAT.BIN" >nul
    move /y "%JOGO%\new_DAT.TBL" "%RAIZ%SAIDA\DAT.TBL" >nul
    echo.
    echo ============================================================
    echo  PRONTO! Os arquivos traduzidos estao na pasta SAIDA:
    echo     SAIDA\DAT.BIN  e  SAIDA\DAT.TBL
    echo  Troque esses dois arquivos na pasta da ISO extraida
    echo  e monte a ISO de novo no ImgBurn.
    echo ============================================================
) else (
    echo ERRO: o DAT.BIN novo nao foi gerado. Mande o log.txt
    dir /b "%JOGO%"
)
goto :fim

:faltando
echo ERRO: coloque o DAT.BIN e o DAT.TBL da sua ISO em ingles dentro da pasta JOGO.
echo       ^(abra a ISO com o 7-Zip ou WinRAR e arraste os dois arquivos^)

:fim
if exist "%RAIZ%saida.log" del "%RAIZ%saida.log"
echo.
pause
