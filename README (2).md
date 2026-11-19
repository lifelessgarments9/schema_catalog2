# Техническая документация: Сервис авторизации ГУИМЦ через BMSTU SSO (OAuth2)

Данный сервис обеспечивает интеграцию Личного кабинета ГУИМЦ с единой системой аутентификации МГТУ им. Н.Э. Баумана по протоколу **OAuth2 (Authorization Code Grant)**.

## 1. Обзор архитектуры

Процесс авторизации реализован по классической схеме с подтверждением владения кодом доступа:

1.  **Redirect**: Сервис генерирует уникальный параметр `state` для защиты от CSRF и перенаправляет пользователя на сервер SSO.
2.  **Callback**: После успешного логина SSO возвращает пользователя на `REDIRECT_URI` с временным кодом (`code`) и тем же `state`.
3.  **Token Exchange**: Сервис отправляет `code` на бэкенд SSO в обмен на `access_token`.
4.  **UserInfo**: Используя полученный токен, сервис запрашивает профиль пользователя для идентификации.

## 2. Техническая конфигурация

Параметры  определяются в файле `settings.py`.

| Константа | Описание                          | Значение (пример) |
| :--- |:----------------------------------| :--- |
| `SSO_CLIENT_ID` | Идентификатор приложения в SSO | `bmstu-guimc` |
| `SSO_CLIENT_SECRET` | Секрет клиента (только backend) | задаётся в `.env` |
| `SSO_REDIRECT_URI` | Callback, зарегистрированный у SSO | `https://lk.guimc.bmstu.ru/fablab/` |
| `SSO_BASE_URL` | База OAuth2 endpoint-ов | `https://sso.bmstu.ru/portal4/oauth2` |
| `APP_URL_PREFIX` | Префикс маршрутов приложения и backend API | `/fablab` |

## 3. Логика работы с сессией

Для обеспечения бесшовного взаимодействия и безопасности используются следующие механизмы:

1.  **Хранение данных**:
    *   Данные `/userinfo` используются для создания или обновления локального пользователя по GUID.
    *   SSO access token хранится только в серверной Django-сессии для server-to-server logout.
    *   В браузер передаются JWT приложения; client secret и SSO access token туда не отправляются.
2.  **CSRF Protection (state)**:
    Перед редиректом на SSO генерируется случайная строка `oauth_state`, которая сохраняется в сессии пользователя. При получении обратного вызова (Callback) система **обязана** сравнить `state` из URL с `state` из сессии. При несовпадении запрос отклоняется (риск атаки Middle-In-The-Middle).

## 4. Исторический лог (старая реализация)

Этот пример сохранён только как история отладки: в нём используются старый callback в корне сайта и старые маршруты. Он не описывает текущий OAuth flow.

<details>
<summary>Просмотр отладочной информации (очищено от секретов)</summary>

```text
--- [DEBUG] Вход в index view ---
--- [DEBUG] GET параметры - code: None, state: None
--- [DEBUG] Код отсутствует, данные пользователя в сессии: None
[04/Apr/2026 14:14:58] "GET / HTTP/1.1" 200 1080

--- [DEBUG] Инициация входа через SSO ---
--- [DEBUG] Сгенерированный state: <GENERATED_STATE_STRING>
--- [DEBUG] Перенаправление на: https://sso.bmstu.ru/portal4/oauth2/authorize?response_type=code&client_id=bmstu-guimc&redirect_uri=https%3A%2F%2Flk.guimc.bmstu.ru%2F&state=<GENERATED_STATE_STRING>
[04/Apr/2026 14:15:00] "GET /login/ HTTP/1.1" 302 0

--- [DEBUG] Вход в index view ---
--- [DEBUG] GET параметры - code: <AUTHORIZATION_CODE>, state: <GENERATED_STATE_STRING>
--- [DEBUG] Сравнение state - получено: <GENERATED_STATE_STRING>, в сессии: <GENERATED_STATE_STRING>
--- [DEBUG] Данные запроса токена: {'grant_type': 'authorization_code', 'code': '<AUTHORIZATION_CODE>', 'client_id': 'bmstu-guimc', 'client_secret': '<CLIENT_SECRET_REDACTED>', 'redirect_uri': 'https://lk.guimc.bmstu.ru/'}
--- [DEBUG] Статус ответа токена: 200
--- [DEBUG] Токены получены: {'access_token': 'eyJhbGciOiJSUzI1Ni...<REDACTED_ACCESS_TOKEN>', 'token_type': 'Bearer', 'expires_in': 172799, 'refresh_token': '<REDACTED_REFRESH_TOKEN>', 'authorizationCode': '<AUTHORIZATION_CODE>', 'person': {'id': 12345, 'guid': '00000000-0000-0000-0000-000000000000', 'name': 'Иванов Иван Иванович', 'firstname': 'Иван', 'lastname': 'Иванов', 'middlename': 'Иванович', 'alias': 'ИУ1-11Б', 'birthdate': '2000-01-01', 'props': [{'scope': '7063111c-397a-46dc-9ecd-8e320ada144e', 'key': 'group_name', 'value': 'ИУ1-11Б'}, {'scope': '7063111c-397a-46dc-9ecd-8e320ada144e', 'key': 'account_type', 'value': 'student'}, {'scope': '7063111c-397a-46dc-9ecd-8e320ada144e', 'key': 'department_uuid', 'value': '11111111-1111-1111-1111-111111111111'}, {'scope': '7063111c-397a-46dc-9ecd-8e320ada144e', 'key': 'department_name', 'value': 'ИУ1'}, {'scope': '7063111c-397a-46dc-9ecd-8e320ada144e', 'key': 'group_uuid', 'value': '22222222-2222-2222-2222-222222222222'}], 'email': 'ivanov@student.bmstu.ru'}}
--- [DEBUG] Access Token: eyJhbGciOiJSUzI1Ni...<REDACTED_ACCESS_TOKEN>
--- [DEBUG] Заголовки запроса UserInfo: {'Authorization': 'Bearer eyJhbGciOiJSUzI1Ni...<REDACTED_ACCESS_TOKEN>'}
--- [DEBUG] Статус ответа UserInfo: 200
--- [DEBUG] Данные пользователя: {'id': 12345, 'guid': '00000000-0000-0000-0000-000000000000', 'name': 'Иванов Иван Иванович', 'alias': 'ИУ1-11Б', 'email': 'ivanov@student.bmstu.ru', 'props': [{'key': 'group_name', 'scope': '7063111c-397a-46dc-9ecd-8e320ada144e', 'value': 'ИУ1-11Б'}, {'key': 'account_type', 'scope': '7063111c-397a-46dc-9ecd-8e320ada144e', 'value': 'student'}, {'key': 'department_uuid', 'scope': '7063111c-397a-46dc-9ecd-8e320ada144e', 'value': '11111111-1111-1111-1111-111111111111'}, {'key': 'department_name', 'scope': '7063111c-397a-46dc-9ecd-8e320ada144e', 'value': 'ИУ1'}, {'key': 'group_uuid', 'scope': '7063111c-397a-46dc-9ecd-8e320ada144e', 'value': '22222222-2222-2222-2222-222222222222'}], 'lastname': 'Иванов', 'birthdate': '2000-01-01', 'firstname': 'Иван', 'middlename': 'Иванович'}
--- [DEBUG] Данные сохранены в сессию. Перенаправление на главную.
[04/Apr/2026 14:15:05] "GET /?code=<AUTHORIZATION_CODE>&state=<GENERATED_STATE_STRING> HTTP/1.1" 302 0

--- [DEBUG] Вход в index view ---
--- [DEBUG] GET параметры - code: None, state: None
--- [DEBUG] Код отсутствует, данные пользователя в сессии: {'id': 12345, 'guid': '00000000-0000-0000-0000-000000000000', 'name': 'Иванов Иван Иванович', 'alias': 'ИУ1-11Б', 'email': 'ivanov@student.bmstu.ru', 'props': [{'key': 'group_name', 'scope': '7063111c-397a-46dc-9ecd-8e320ada144e', 'value': 'ИУ1-11Б'}, {'key': 'account_type', 'scope': '7063111c-397a-46dc-9ecd-8e320ada144e', 'value': 'student'}, {'key': 'department_uuid', 'scope': '7063111c-397a-46dc-9ecd-8e320ada144e', 'value': '11111111-1111-1111-1111-111111111111'}, {'key': 'department_name', 'scope': '7063111c-397a-46dc-9ecd-8e320ada144e', 'value': 'ИУ1'}, {'key': 'group_uuid', 'scope': '7063111c-397a-46dc-9ecd-8e320ada144e', 'value': '22222222-2222-2222-2222-222222222222'}], 'lastname': 'Иванов', 'birthdate': '2000-01-01', 'firstname': 'Иван', 'middlename': 'Иванович'}
[04/Apr/2026 14:15:05] "GET / HTTP/1.1" 200 2681
```
</details>

---
## 🚀 Быстрый запуск (Docker)

Для запуска проекта на любой машине:

1.  **Запустите Docker**:
    ```bash
    sudo docker-compose up --build
    ```

2.  Убедитесь, что reverse proxy направляет `/fablab/` во frontend, API-пути с этим prefix — в backend, и передаёт `X-Forwarded-Proto: https`.
3.  **Откройте сайт**: [https://lk.guimc.bmstu.ru/fablab/](https://lk.guimc.bmstu.ru/fablab/)

---

### Размещение под URL-префиксом

Для размещения под `/fablab/` задайте `APP_URL_PREFIX=/fablab`, `FRONTEND_URL=https://lk.guimc.bmstu.ru/fablab` и `REACT_APP_API_URL=https://lk.guimc.bmstu.ru/fablab`. Reverse proxy должен направлять `/fablab/` во frontend, а backend API пути под `/fablab/` — в Django, сохраняя prefix.

---

## HTTPS и reverse proxy

TLS должен завершаться на reverse proxy, который направляет `/fablab/` во frontend, а маршруты `/fablab/accounts/`, `/fablab/catalog/`, `/fablab/rental/`, `/fablab/ai/`, `/fablab/admin/` и `/fablab/api/` в Django, сохраняя `/fablab` в request path. Для production proxy также должен передавать `X-Forwarded-Proto: https`.

### 🔴 Ошибка "invalid_client"
Если SSO возвращает `invalid_client` с сообщением о несовпадении `redirect_uri`, убедитесь, что `SSO_REDIRECT_URI` в backend `.env` точно равен `https://lk.guimc.bmstu.ru/fablab/` и что этот адрес разрешён для `SSO_CLIENT_ID` на стороне BMSTU SSO.
