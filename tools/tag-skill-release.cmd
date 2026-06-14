@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tag-skill-release.ps1" %*
