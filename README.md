# Chore wars: the clone wars runbook

To run this application:
```
flask --debug run
```

## Deploy
```
ssh chorebot@192.168.1.[ending ip number] '/home/chorebot/code/chore-wars-clone/upgrade.sh'
```
## Troubleshooting
After unplugging and plugging router back in, the site was down. The IP mapping was retained, but docker daemon needed to be started (`sudo service docker start`) and clock resynced (`rc-service ntpd start`). Then, I ran the upgrade script to restart the container.

## Database
### Bulk update rows

I had to download sqlite3 cli: `sudo apk add sqlite sqlite-libs`.

Launch the cli with: `sudo sqlite3 /var/chore-wars-db-instance/database.db` and run commands like this:  `UPDATE claim SET chore_id = 9 WHERE chore_id = 2;`
### Plug and play queries
#### Total claim count by chore for each user.
```
SELECT 
    c.chore_id,
    ch.name AS chore_name,
    c.completed_by,
    COUNT(*) AS total_claims
FROM claim c
JOIN chore ch ON c.chore_id = ch.id
-- by year
-- WHERE strftime('%Y', c.completed_at) = '2025'
-- last 30 days
-- WHERE date(c.completed_at) >= date('now', '-30 day') 
GROUP BY c.chore_id, ch.name, c.completed_by
ORDER BY c.chore_id, c.completed_by;
```
