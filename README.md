# FightIQ Data Engine Ultra V3

Backend GitHub Actions gratuit pour alimenter FightIQ avec les données UFCStats.

## Objectif

Récupérer, structurer et exporter :

- fighters
- fighter_stats
- events
- fights
- fight_stats
- rankings placeholder
- predictions placeholder
- analytics basiques

## Premier test conseillé

GitHub > Actions > FightIQ Data Engine Ultra > Run workflow :

- upload_to_supabase: false
- max_events: 5
- max_fighters: 20
- max_fights: 50

Ensuite télécharge l’artifact `fightiq-ultra-exports`.

## Passage en production

Quand le test est OK :

1. Ajoute les secrets GitHub :
   - SUPABASE_URL
   - SUPABASE_SERVICE_ROLE_KEY

2. Lance avec :
   - upload_to_supabase: true
   - max_events: vide
   - max_fighters: vide
   - max_fights: vide

## CSV générés

- exports/fighters.csv
- exports/fighter_stats.csv
- exports/events.csv
- exports/fights.csv
- exports/fight_stats.csv
- exports/rankings.csv
- exports/predictions.csv
- exports/import_report.json

## Important

Cette version est beaucoup plus complète, mais UFCStats peut changer sa structure HTML.
Si une table sort vide, il faudra ajuster le parser concerné.
