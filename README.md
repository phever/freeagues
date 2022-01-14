# freeagues
django website for the free phoenix leagues
anyone is free to copy these for their own use, it includes a built-in WER results parser

### NOTE: that the WER parser has not been updated to work with the new Web-App. ☹️

*just the git repo for a django site being hosted through heroku @ leagues.phoenixcomics.ca*

### installation (from a terminal)
#### download
```bash
git clone https://github.com/phever/freeagues.git
cd freeagues
```

#### edit settings & create database
comment out the ```django_heroku.settings(locals())``` line at the bottom of the *settings.py* file
```
python manage.py migrate
```
#### then edit away!
#### once finished editing
uncomment the bottom line so that ```django_heroku.settings(locals())``` is the last line in the *settings.py* file.

host the Procfile via Heroku (aka code on SourceLair) or `python manage.py migrate && python manage.py runserver`
