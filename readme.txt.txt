git clone https://github.com/lifelessgarments9/schema_catalog2
cd schema_catalog2

env

[ Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass ]

python -m venv venv
.\venv\Scripts\activate

cd backend
pip install -r requirements.txt

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver

cd \frontend
npm install
npm start