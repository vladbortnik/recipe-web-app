# recipe-web-app

## DB Init (on local machine)

```bash
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

## Docker Logs

```bash
docker-compose logs web
docker-compose logs db
```
