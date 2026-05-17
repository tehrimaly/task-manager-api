New-Item -Path "Procfile" -ItemType File -Force
Set-Content -Path "Procfile" -Value "web: gunicorn app:app --bind 0.0.0.0:`$PORT"