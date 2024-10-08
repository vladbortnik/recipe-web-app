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

## Access Docker Container Terminal

1. **List running containers**:

   ```sh
   docker ps
   ```

2. **Access the terminal**:

   ```sh
   docker exec -it <container_id_or_name> /bin/bash
   ```

   If the container uses `sh` instead of `bash`, use:

   ```sh
   docker exec -it <container_id_or_name> /bin/sh
   ```
