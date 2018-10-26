# freeages
django website for the free phoenix leagues

*just the git repo for a django site being developed on SourceLair*

### installation (from a terminal)
#### download
```bash
git clone https://github.com/phever/freeagues.git
cd freeagues
```

#### create database
```
python manage.py migrate
```
#### then either
host the Procfile via Heroku (aka code on SourceLair) or `python manage.py migrate && python manage.py runserver`
