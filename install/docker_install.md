# CytoBulk Installation — Docker Version

## 1.2 Docker installation

First, verify that Docker is installed and working:

```bash
docker --version
docker info
```

Then pull the CytoBulk Docker image:

```bash
docker pull kristawang/cytobulk:1.0.0
```

Verify the image is available locally:

```bash
docker images | grep cytobulk
```

You should see output similar to:

```
REPOSITORY           TAG       IMAGE ID       SIZE
kristawang/cytobulk  1.0.0     <image_id>     <size>
```

## 1.3 Troubleshooting

If you encounter `OOM killer` or other out-of-memory issues when running the container, you can increase the memory limit by adding `--memory=xxx` to the `docker run` command.

For example:

```bash
docker run --memory=16g ...
```

You can adjust the value according to your machine, such as `8g`, `16g`, or `32g`.

