# iptv-proxy
Simple Flask proxy app for m3u files. This should be used alongside a VPN container. If you don't have a VPN, then there's no point of using an m3u proxy.

# Docker

```
version: '3'

services:
  iptv_proxy:
    image: parkerr1992/iptv-proxy
    container_name: iptv_proxy
    restart: unless-stopped
    ports:
      - 8080:8080
    environment:
      - M3U_LOCATION= # Required. Either a path or URL.
      - RELOAD_INTERVAL_MIN=60 # Not required and defaults to 60. This is used to update the /static directory with the latest m3u file.
      - LISTEN_PORT=8080
```
