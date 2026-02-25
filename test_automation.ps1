$headers = @{"Content-Type"="application/json"; "x-internal-key"="neurocore-internal-key"}
$body = @{"host"="PROD-01"; "severity"="High"; "subject"="CPU high"; "message"="CPU 99%"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/alerts/zabbix" -Method Post -Headers $headers -Body $body
