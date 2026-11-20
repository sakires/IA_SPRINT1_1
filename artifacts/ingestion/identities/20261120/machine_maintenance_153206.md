# Identité : machine_maintenance

- Source: Datas/machine.sql
- Filesize: 22.41 Ko
- ProcessBeginAt: 15:32:06
- ProcessEndAt: 15:32:06
- Charset: utf-8
- Rows Number: 115
- Cols Number: 9

## Colonnes

| Colname | Infered Type |
| ------- | ------------ |
| maintenance_id | IDENTITY |
| machine_code | TEXT |
| maintenance_at | DATE |
| maintenance_type | TEXT |
| action_type | TEXT |
| component | TEXT |
| description | TEXT |
| related_incident_id | IDENTITY |
| duration_hours | NUMERIC |

## Statistiques

| Colname | Min | Max | Mean | Median |
| ------- | --- | --- | ---- | ------ |
| maintenance_at | 2025-06-15 06:00:00+00:00 | 2026-05-30 22:00:00+00:00 | - | - |
| duration_hours | 1.0 | 8.0 | 2.943 | 2.64 |
