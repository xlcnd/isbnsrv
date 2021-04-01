## How to install and run?

First you need to install Docker in your system and download and unzip [this file](https://github.com/xlcnd/isbnsrv/archive/refs/tags/v1.1.5.zip). Then enter in a terminal (inside directory `isbnsrv-1.1.5`):

```
$ docker build --tag="isbnsrv:1.1.5" .
$ docker run -d -p 8080:8080 isbnsrv:1.1.5
```

(it exposes port 8080). Now read the [documentation](https://github.com/xlcnd/isbnsrv/tree/v1.1.5#readme).


## What's new?

1. Fix documentation!
