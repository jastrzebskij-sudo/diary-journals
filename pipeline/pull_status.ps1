# pull_status.ps1 - copy the brokkr orchestrator status into the Diary folder so Obsidian shows it. Read-only on brokkr.
#   .\pull_status.ps1        (run on loki)    Output: D:\Claude\Projects\Diary\STATUS-PIPELINE.md
scp -q brokkr-agent:/srv/tts-out/pipe/STATUS-PIPELINE.md D:\Claude\Projects\Diary\STATUS-PIPELINE.md
scp -q brokkr-agent:/srv/tts-out/pipe/ledger.jsonl D:\Claude\Projects\Diary\pipeline\ledger-brokkr.jsonl
Get-Content D:\Claude\Projects\Diary\STATUS-PIPELINE.md -TotalCount 14
