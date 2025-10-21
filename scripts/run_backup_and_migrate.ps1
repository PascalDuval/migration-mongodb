# run_backup_and_migrate.ps1
# Script PowerShell pour :
# 1) sauvegarder la collection mediccrud en JSONL
# 2) supprimer la collection
# 3) effectuer un dry-run de l'import
# 4) proposer de lancer la migration complète

param(
    [string]$Uri = "mongodb://localhost:27017",
    [string]$Db = "FirstTry",
    [string]$Collection = "mediccrud",
    [string]$Python = "./.venv/Scripts/python.exe"
)

Write-Host '1) Sauvegarde et suppression de la collection ' $Db '.' $Collection
& $Python "scripts/backup_and_drop.py" --uri $Uri --db $Db --collection $Collection

Write-Host '`n2) Dry-run de l''import (conversion sans insertion)'
& $Python "scripts/migration_crud.py" import_csv --dry --file ../data/healthcare_dataset_purge.csv

$confirm = Read-Host '`nVoulez-vous lancer la migration complete maintenant ? (o/N)'
if ($confirm -match '^(o|O|y|Y)') {
    Write-Host 'Lancement de la migration complete...'
    & $Python 'scripts/migration_crud.py' import_csv --file ../data/healthcare_dataset_purge.csv
    Write-Host 'Migration terminee. Pensez a creer les index : python scripts/migration_crud.py create_indexes'
} else {
    Write-Host 'Migration annulee. Les donnees sauvegardees sont disponibles dans le dossier data/.'
}
