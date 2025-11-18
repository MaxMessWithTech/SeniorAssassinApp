## How to Start
```
python3 -m venv venv
source venv/bin/activate (Mac)
venv\Scripts\activate (Windows)
pip3 install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```


## To start over:
```
delete "db.sqlite3"
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver
```

Update the "SeniorAssassinTeams.csv" file with correct team ids, names, and members
Navigate to "http://127.0.0.1:8000/add-things"
Navigate to "http://127.0.0.1:8000/admin/assignments/round/add/", and create your first round
Navigate to "http://127.0.0.1:8000/create-pairings/"