# Git, Python и Kubernetes

`app.py` считает непустые строки в UTF-8 файле. Для запуска достаточно Python 3, внешних пакетов нет.

```powershell
py app.py sample.txt
py app.py sample.txt --debug
py app.py missing.txt
$LASTEXITCODE
```

В первом запуске ожидается `INFO Non-empty lines: 2`. С `--debug` добавляется сообщение о чтении файла. Для отсутствующего файла ожидается `ERROR` и код выхода 1.
