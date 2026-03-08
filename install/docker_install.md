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

