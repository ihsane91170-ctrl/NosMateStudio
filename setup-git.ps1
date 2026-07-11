param(
    [string]$RemoteUrl = "https://github.com/ihsane91170-ctrl/NosMateStudio.git"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".git")) {
    git init
}

git branch -M main
git remote remove origin 2>$null
git remote add origin $RemoteUrl

git add .
git commit -m "chore: initialize NosMate Studio project"

git push -u origin main

git checkout -b develop
git push -u origin develop

Write-Host ""
Write-Host "Initialisation terminée."
Write-Host "Branche active : develop"
Write-Host "Prochaine étape : git checkout -b feature/US001-detection-nostale"
