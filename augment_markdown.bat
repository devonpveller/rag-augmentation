@echo off
REM Batch script to augment markdown files with header blocks
REM Usage: augment_markdown.bat [input_folder] [output_folder]

setlocal

REM Default paths
set INPUT_PATH=I:\_RAG
set OUTPUT_PATH=I:\_RAG_augmented

REM Override with command line arguments if provided
if not "%1"=="" set INPUT_PATH=%1
if not "%2"=="" set OUTPUT_PATH=%2

echo Augmenting markdown files...
echo Input folder: %INPUT_PATH%
echo Output folder: %OUTPUT_PATH%
echo.

python "I:\_RAG\augment_markdown.py" --in "%INPUT_PATH%" --out "%OUTPUT_PATH%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Successfully augmented all markdown files!
    echo Output saved to: %OUTPUT_PATH%
) else (
    echo.
    echo Error occurred during processing. Please check the output above.
)

pause
