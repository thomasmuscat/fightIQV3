# Installation GitHub

1. Upload tout le contenu dans ton repository GitHub.
2. Vérifie que `.github/workflows/fightiq-sync.yml` existe.
3. Va dans Actions.
4. Lance `FightIQ Data Engine Ultra`.

Premier test :
- upload_to_supabase: false
- max_events: 5
- max_fighters: 20
- max_fights: 50

Si OK, production :
- upload_to_supabase: true
- max_events: vide
- max_fighters: vide
- max_fights: vide
