in root folder:

1. fill env

[ Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass ]

2. python -m venv venv
3. .\venv\Scripts\activate

4. cd backend
5. pip install -r requirements.txt

6. python manage.py migrate

7. python manage.py createsuperuser

8. python manage.py runserver

9. cd \frontend
10. npm install
11. npm start
