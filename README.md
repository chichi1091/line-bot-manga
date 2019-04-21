# LINE BOT Manga

## Create Local Development environment

```shell
$ python -m venv env
$ source env/bin/activate
(env) $ pip install flask
(env) $ pip install celery
(env) $ pip install gunicorn
(env) $ pip install line-bot-sdk
(env) $ pip install beautifulsoup4

(env) $ pip freeze > requirements.txt

(env) $ echo Python 3.7.2 >runtime.txt
(env) $ echo web: gunicorn app:app --log-file=- > Procfile
(env) $ touch server.py
```