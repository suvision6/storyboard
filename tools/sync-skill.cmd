@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0sync-skill.ps1" %*
