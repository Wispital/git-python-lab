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
