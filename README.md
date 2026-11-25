# Git, Python и Kubernetes

`app.py` считает непустые строки в UTF-8 файле. Для запуска достаточно Python 3, внешних пакетов нет.

```powershell
py app.py sample.txt
py app.py sample.txt --debug
py app.py missing.txt
$LASTEXITCODE
```

В первом запуске ожидается `INFO Non-empty lines: 2`. С `--debug` добавляется сообщение о чтении файла. Для отсутствующего файла ожидается `ERROR` и код выхода 1.

## Docker и Kubernetes

Из корня проекта соберите образ и запустите скрипт в контейнере:

```powershell
docker build -t git-python-lab:local .
docker run --rm git-python-lab:local sample.txt --debug
```

Для запуска Job нужен локальный кластер Docker Desktop с Kubeadm. Образ должен быть доступен узлу локально: в манифесте задано `imagePullPolicy: Never`.

```powershell
kubectl --context docker-desktop apply -f job.yaml
kubectl --context docker-desktop wait --for=condition=complete job/line-counter --timeout=90s
kubectl --context docker-desktop logs job/line-counter
```

В логах ожидаются `DEBUG Reading sample.txt` и `INFO Non-empty lines: 2`. Чтобы удалить учебную Job и её Pod, выполните:

```powershell
kubectl --context docker-desktop delete -f job.yaml
```

## Minikube и Helm

Запустите Docker Desktop в режиме Linux-контейнеров. Из корня проекта
выполните команды с Minikube и Helm, доступными в PowerShell:

```powershell
minikube start --driver=docker
docker build -t git-python-lab:local .
minikube image load git-python-lab:local
helm lint chart
helm install line-counter ./chart --kube-context minikube
kubectl --context minikube wait --for=condition=complete job/line-counter --timeout=90s
kubectl --context minikube logs job/line-counter
```

Откройте веб-интерфейс командой `minikube dashboard` в отдельном окне.
В Dashboard выберите namespace `default` и найдите Job `line-counter`.

## PostgreSQL и SQL

База работает отдельно от Helm Job. Service `postgres` доступен внутри
кластера, а StatefulSet хранит данные на PVC. Пример рассчитан на локальную
учебную базу: Python подключается с учётной записью из того же Secret.

Из корня проекта, в PowerShell, на запущенном Minikube:

```powershell
$mini = (Resolve-Path '..\..\work\kube-tools\minikube.exe').Path
$helm = (Resolve-Path '..\..\work\kube-tools\windows-amd64\helm.exe').Path
kubectl --context minikube create namespace sql-lab
$pgPassword = [guid]::NewGuid().ToString('N')
kubectl --context minikube -n sql-lab create secret generic postgres-login --from-literal=POSTGRES_DB=linecounter --from-literal=POSTGRES_USER=linecounter --from-literal="POSTGRES_PASSWORD=$pgPassword"
Remove-Variable pgPassword
kubectl --context minikube -n sql-lab apply -f postgres/database.yaml
kubectl --context minikube -n sql-lab rollout status statefulset/postgres --timeout=180s
```

Создайте таблицу и добавьте четыре тестовые записи. Повторный запуск
`seed.sql` добавит ещё четыре записи.

```powershell
Get-Content postgres/schema.sql -Raw | kubectl --context minikube -n sql-lab exec -i postgres-0 -- psql -v ON_ERROR_STOP=1 -U linecounter -d linecounter
Get-Content postgres/seed.sql -Raw | kubectl --context minikube -n sql-lab exec -i postgres-0 -- psql -v ON_ERROR_STOP=1 -U linecounter -d linecounter
```

Соберите новый образ, загрузите его в Minikube и выполните Helm Job:

```powershell
docker build -t git-python-lab:db .
& $mini image load git-python-lab:db
& $helm install line-counter-db ./chart -f chart/postgres-values.yaml --kube-context minikube -n sql-lab
kubectl --context minikube -n sql-lab wait --for=condition=complete job/line-counter-db --timeout=90s
kubectl --context minikube -n sql-lab logs job/line-counter-db
```

В логах ожидается `INFO Result saved to PostgreSQL`. Выполните запросы:

```powershell
Get-Content postgres/queries.sql -Raw | kubectl --context minikube -n sql-lab exec -i postgres-0 -- psql -v ON_ERROR_STOP=1 -U linecounter -d linecounter
```

После первого запуска в таблице должно быть пять строк. Для `sample.txt`
ожидается `non_empty_lines = 2`. Для `notes.txt` запрос с группировкой
должен вернуть два запуска со средним числом строк 4.

## Веб-интерфейс, Python API и Adminer

После развёртывания базы и создания таблицы из предыдущего раздела:

```powershell
$mini = (Resolve-Path '..\..\work\kube-tools\minikube.exe').Path
docker build -t git-python-lab:web .
& $mini image load git-python-lab:web
kubectl --context minikube -n sql-lab apply -k web
kubectl --context minikube -n sql-lab rollout status deployment/line-counter-api --timeout=120s
kubectl --context minikube -n sql-lab rollout status deployment/line-counter-web --timeout=120s
kubectl --context minikube -n sql-lab rollout status deployment/adminer --timeout=120s
kubectl --context minikube -n sql-lab get pods,services
```

Фронтенд в отдельном Pod Nginx отправляет запросы через Service
`line-counter-api` в Python API. API выполняет SELECT в PostgreSQL и
возвращает до 100 последних записей. В двух отдельных окнах PowerShell
откройте локальный доступ к фронтенду и Adminer:

```powershell
kubectl --context minikube -n sql-lab port-forward svc/line-counter-web 8080:80
```

```powershell
kubectl --context minikube -n sql-lab port-forward svc/adminer 8081:8080
```

Откройте фронтенд по адресу `http://localhost:8080`. JSON API доступен
по адресу `http://localhost:8080/api/line-counts`.

В Adminer по адресу `http://localhost:8081` выберите PostgreSQL,
укажите сервер `postgres`, пользователя и базу `linecounter`.
Пароль из Secret можно получить локально в третьем окне PowerShell:

```powershell
$encoded = kubectl --context minikube -n sql-lab get secret postgres-login -o 'jsonpath={.data.POSTGRES_PASSWORD}'
[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($encoded))
```

В разделе **SQL command** вручную напишите запросы к `line_counts`:

1. Найдите строку для `sample.txt`.
2. Выведите записи с числом строк не меньше трёх, от большего к меньшему.
3. Сгруппируйте по имени файла, посчитайте количество запусков и среднее.
   Через HAVING оставьте только файлы с несколькими запусками.
4. Добавьте учебную запись `manual.txt` с числом строк 7 через INSERT,
   затем обновите фронтенд и найдите её.

Для остановки каждого port-forward нажмите Ctrl+C в соответствующем окне.
