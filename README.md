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

To access the terminal inside a running Docker container, you can use the `docker exec` command. Here are the steps:

1. **List running containers** to find the container ID or name:

   ```sh
   docker ps
   ```

2. **Access the terminal** of the running container using its container ID or name:

   ```sh
   docker exec -it <container_id_or_name> /bin/bash
   ```

   If the container uses `sh` instead of `bash`, use:

   ```sh
   docker exec -it <container_id_or_name> /bin/sh
   ```

For example, if your container ID is `abc123`, you would run:

```sh
docker exec -it abc123 /bin/bash
```

This will open an interactive terminal session inside the running Docker container.
