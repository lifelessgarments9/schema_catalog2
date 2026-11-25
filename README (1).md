# BMSTU SSO Authentication Service (GUIMC)

Сервис авторизации через **МГТУ им. Н.Э. Баумана SSO (OAuth2)** для ЛК ГУИМЦ. 

### Архитектура и Реализация

Авторизация реализована по стандартному протоколу **OAuth2 (Authorization Code Grant)**. Весь процесс разделен на 3 этапа:

1.  **Авторизация (Redirect):** Пользователь нажимает «Войти», сервис генерирует уникальный `state` (для защиты от CSRF) и перенаправляет пользователя на `sso.bmstu.ru/portal4/oauth2/authorize` с `client_id` и `redirect_uri`.
    ```http
    GET https://sso.bmstu.ru/portal4/oauth2/authorize?response_type=code&client_id=bmstu-guimc&redirect_uri=https%3A%2F%2Flk.guimc.bmstu.ru%2Ffablab%2Fapi%2Faccounts%2Fsso%2Fcallback%2F&state=random_state_string
    ```

2.  **Callback и получение токена:** После успешного входа SSO возвращает браузер GET-запросом напрямую на Django callback с временным кодом (`code`) и `state`. Django сверяет `state`, меняет код на токен server-to-server и запрашивает профиль пользователя.
    ```http
    POST /portal4/oauth2/token
    Content-Type: application/x-www-form-urlencoded

    grant_type=authorization_code&code=AUTHORIZATION_CODE_HERE&client_id=bmstu-guimc&client_secret=SECRET&redirect_uri=https://lk.guimc.bmstu.ru/fablab/api/accounts/sso/callback/
    ```
    
    *Пример успешного ответа:*
    ```json
    {
      "access_token": "eyJhbGciOiJSUzI1Ni...",
      "token_type": "Bearer",
      "expires_in": 172799,
      "refresh_token": "..."
    }
    ```

3.  **Получение данных пользователя:** Используя полученный токен, сервис запрашивает информацию о профиле пользователя (ФИО, почта, группа и т.д.) через эндпоинт `userinfo`.
    ```http
    GET /portal4/oauth2/userinfo
    Authorization: Bearer eyJhbGciOiJSUzI1Ni...
    ```
    
#### Диаграмма последовательности (OAuth2 Flow)

```mermaid
sequenceDiagram
    participant User as Пользователь (Браузер)
    participant Client as Сервис ГУИМЦ (lk.guimc.bmstu.ru)
    participant SSO as BMSTU SSO (sso.bmstu.ru)

    User->>Client: 1. Нажатие на кнопку "Войти" (GET /login/)
    Note right of Client: Генерация state (CSRF Protection)
    Client->>User: 2. 302 Redirect на SSO Authorize URL
    Note over Client, User: Fields: response_type=code, client_id, redirect_uri, state

    User->>SSO: 3. Ввод логина и пароля МГТУ
    SSO-->>Client: 4. 302 Redirect на Django callback с code и state
    Note right of Client: Django сверяет state с сессией

    rect rgb(150, 150, 150)
        Note right of Client: Обмен кода на токен (Backend-to-Backend)
        Client->>SSO: 6. POST /portal4/oauth2/token
        SSO-->>Client: 7. JSON Response (access_token)
    end

    rect rgb(150, 150, 150)
        Note right of Client: Получение данных пользователя
        Client->>SSO: 8. GET /portal4/oauth2/userinfo
        SSO-->>Client: 9. JSON Response (fio, email, group, etc.)
    end

        Client->>User: 10. Redirect на React с одноразовым ticket во fragment
        User->>Client: 11. React отправляет ticket на backend
        Client->>User: 12. Backend выдаёт локальные JWT приложения
```

### Спецификация данных пользователя

JSON Web Token - после обмена кода сервис получает JWT. Ниже представлен пример payload для типичного пользователя:

```json
{
  "sub": "12345",
  "guid": "00000000-0000-0000-0000-000000000000",
  "name": "Иванов Иван Иванович",
  "group": "ИУ1-11Б",
  "iat": 1712232000,
  "nbf": 1712232000,
  "exp": 1712235600
}
```

Userinfo - полные данные, которые приходят от SSO МГТУ.  Они содержат массив props, который важен для определения учебной группы и кафедры:

```json
{
  "id": 12345,
  "guid": "00000000-0000-0000-0000-000000000000",
  "name": "Иванов Иван Иванович",
  "firstname": "Иван",
  "lastname": "Иванов",
  "middlename": "Иванович",
  "alias": "ИУ1-11Б",
  "email": "ivanov@student.bmstu.ru",
  "birthdate": "2000-01-01",
  "props": [
    {
      "key": "group_name",
      "value": "ИУ1-11Б",
      "scope": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    },
    {
      "key": "account_type",
      "value": "student",
      "scope": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    },
    {
      "key": "department_name",
      "value": "ИУ1",
      "scope": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    },
    {
      "key": "department_uuid",
      "value": "11111111-1111-1111-1111-111111111111",
      "scope": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    },
    {
      "key": "group_uuid",
      "value": "22222222-2222-2222-2222-222222222222",
      "scope": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    }
  ]
}
```


### Ключевые файлы:

*   [views.py](../examples/bmstu_sso/auth_app/views.py): Основная логика обмена кодами и токенами.
*   [settings.py](../examples/bmstu_sso/bmstu_auth_project/settings.py): Конфигурация клиента (ID, Secret, URL-адреса SSO).
*   [index.html](../examples/bmstu_sso/auth_app/templates/auth_app/index.html): Простой интерфейс для отображения данных пользователя.