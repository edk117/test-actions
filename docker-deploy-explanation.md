# Объяснение workflow docker-deploy.yml

Файл `.github/workflows/docker-deploy.yml` описывает автоматический процесс сборки Docker-образа и деплоя приложения на удаленный сервер.

Workflow запускается при каждом `push` в ветку `main`.

## Общая схема

1. GitHub Actions получает свежий код из репозитория.
2. Собирает Docker-образ проекта.
3. Загружает образ в GitHub Container Registry.
4. Подключается к удаленному серверу по SSH.
5. На сервере скачивает свежий Docker-образ.
6. Останавливает старый контейнер.
7. Запускает новый контейнер с обновленным приложением.

## Общие переменные

В workflow заданы общие переменные:

```yaml
REGISTRY: ghcr.io
IMAGE_TAG: latest
CONTAINER_NAME: fastapi-time-api
```

`REGISTRY` указывает, что Docker-образ хранится в GitHub Container Registry.

`IMAGE_TAG` задает тег образа. В текущем примере используется `latest`.

`CONTAINER_NAME` задает имя контейнера на удаленном сервере.

## Job build-and-push

Первая job называется `build-and-push`.

Она отвечает за сборку Docker-образа и отправку этого образа в GitHub Container Registry.

### Checkout repository

На этом шаге GitHub Actions скачивает код репозитория:

```yaml
uses: actions/checkout@v4
```

Без этого шага workflow не увидит файлы проекта, включая `Dockerfile`.

### Prepare image name

На этом шаге имя репозитория приводится к нижнему регистру:

```bash
echo "image_name=${GITHUB_REPOSITORY,,}" >> "$GITHUB_OUTPUT"
```

Это нужно потому, что GitHub Container Registry ожидает имя образа в нижнем регистре.

Например:

```text
Owner/MyRepo
```

превратится в:

```text
owner/myrepo
```

### Login to GitHub Container Registry

На этом шаге workflow логинится в GHCR:

```yaml
uses: docker/login-action@v3
```

Для логина используется встроенный GitHub token:

```yaml
password: ${{ secrets.GITHUB_TOKEN }}
```

Он позволяет workflow загрузить Docker-образ в registry.

### Build and push image

На этом шаге Docker-образ собирается и отправляется в GHCR:

```yaml
uses: docker/build-push-action@v6
```

Параметр:

```yaml
push: true
```

означает, что после сборки образ нужно сразу загрузить в registry.

Итоговый образ будет иметь примерно такой адрес:

```text
ghcr.io/owner/repository:latest
```

## Job deploy

Вторая job называется `deploy`.

Она запускается только после успешного завершения `build-and-push`:

```yaml
needs: build-and-push
```

Эта job подключается к удаленному серверу и разворачивает свежий Docker-образ.

## Настройка SSH

На шаге `Configure SSH key` workflow создает SSH-ключ из GitHub Secret:

```yaml
SSH_PRIVATE_KEY: ${{ secrets.SERVER_SSH_KEY }}
```

Затем ключ сохраняется в файл:

```bash
~/.ssh/deploy_key
```

После этого добавляется сервер в список известных SSH-хостов:

```bash
ssh-keyscan -p "$SERVER_PORT" -H "$SERVER_HOST" >> ~/.ssh/known_hosts
```

Это нужно, чтобы GitHub Actions мог подключиться к серверу без ручного подтверждения fingerprint.

## Деплой на сервер

На шаге `Pull and run image on server` workflow подключается к серверу по SSH:

```bash
ssh -i ~/.ssh/deploy_key -p "$SERVER_PORT" "$SERVER_USER@$SERVER_HOST"
```

Все данные подключения берутся из GitHub Secrets:

```text
SERVER_HOST
SERVER_PORT
SERVER_USER
SERVER_SSH_KEY
```

## Что происходит на сервере

После подключения к серверу выполняются Docker-команды.

Сначала сервер логинится в GitHub Container Registry:

```bash
echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USERNAME" --password-stdin
```

Для этого используются секреты:

```text
GHCR_USERNAME
GHCR_TOKEN
```

Затем сервер скачивает свежий образ:

```bash
docker pull "$IMAGE_NAME:$IMAGE_TAG"
```

После этого старый контейнер останавливается:

```bash
docker stop "$CONTAINER_NAME" || true
```

И удаляется:

```bash
docker rm "$CONTAINER_NAME" || true
```

`|| true` нужен для того, чтобы команда не сломала деплой, если контейнера еще нет.

Затем запускается новый контейнер:

```bash
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  -p 8000:8000 \
  "$IMAGE_NAME:$IMAGE_TAG"
```

Порт `8000` на сервере пробрасывается в порт `8000` внутри контейнера.

После запуска удаляются неиспользуемые Docker-образы:

```bash
docker image prune -f
```

Это помогает не накапливать старые слои и образы на сервере.

## Необходимые GitHub Secrets

Для работы workflow нужно добавить следующие секреты в настройках GitHub-репозитория:

```text
SERVER_HOST
SERVER_PORT
SERVER_USER
SERVER_SSH_KEY
GHCR_USERNAME
GHCR_TOKEN
```

`SERVER_HOST` - IP-адрес или домен удаленного сервера.

`SERVER_PORT` - SSH-порт сервера, обычно `22`.

`SERVER_USER` - пользователь на сервере.

`SERVER_SSH_KEY` - приватный SSH-ключ для подключения.

`GHCR_USERNAME` - GitHub username или владелец токена.

`GHCR_TOKEN` - GitHub token с правом `read:packages`.

## Что должно быть на сервере

На удаленном сервере должен быть установлен Docker.

Пользователь, под которым выполняется SSH-подключение, должен иметь право запускать Docker-команды.

Приложение после деплоя будет доступно на порту `8000`, если этот порт открыт на сервере.
