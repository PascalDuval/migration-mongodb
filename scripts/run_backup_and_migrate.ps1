# run_backup_and_migrate.ps1
# Script PowerShell pour :
# 1) sauvegarder la collection mediccrud en JSONL
# 2) supprimer la collection
# 3) effectuer un dry-run de l'import
# 4) proposer de lancer la migration complète

param(
    [string]$Uri = $null,
    [string]$Db = "FirstTry",
    [string]$Collection = "mediccrud",
    [string]$Python = "./.venv/Scripts/python.exe"
)

# Resolve URI from environment if not provided
if (-not $Uri -or $Uri.Trim().Length -eq 0) {
    if ($Env:MONGODB_URI) {
        $Uri = $Env:MONGODB_URI
    } elseif ($Env:MONGO_URI_RW) {
        $Uri = $Env:MONGO_URI_RW
    } elseif ($Env:MONGO_URI) {
        $Uri = $Env:MONGO_URI
    } elseif ($Env:MONGO_APP_USERNAME -and $Env:MONGO_APP_PASSWORD -and $Env:MONGO_DB) {
        $host = if ($Env:MONGO_HOST) { $Env:MONGO_HOST } else { 'localhost' }
        $port = if ($Env:MONGO_PORT) { $Env:MONGO_PORT } else { '27017' }
        $Uri = "mongodb://${Env:MONGO_APP_USERNAME}:${Env:MONGO_APP_PASSWORD}@$host:$port/${Env:MONGO_DB}?authSource=${Env:MONGO_DB}"
    } else {
        $Uri = "mongodb://localhost:27017"
    }
}

Write-Host '1) Sauvegarde et suppression de la collection ' $Db '.' $Collection
& $Python "scripts/backup_and_drop.py" --uri $Uri --db $Db --collection $Collection

Write-Host '`n2) Dry-run de l''import (conversion sans insertion)'
& $Python "scripts/migration_crud.py" import_csv --dry --file data/healthcare_dataset_purge.csv

$confirm = Read-Host '`nVoulez-vous lancer la migration complete maintenant ? (o/N)'
if ($confirm -match '^(o|O|y|Y)') {
    Write-Host 'Lancement de la migration complete...'
    & $Python 'scripts/migration_crud.py' import_csv --file data/healthcare_dataset_purge.csv
    Write-Host 'Migration terminee.'
} else {
    Write-Host 'Migration annulee. Les donnees sauvegardees sont disponibles dans le dossier data/.'
}
