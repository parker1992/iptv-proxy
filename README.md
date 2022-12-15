# iptv-proxy
Simple Flask proxy app for m3u files. This should be used alongside a VPN container. If you don't have a VPN, then there's no point of using an m3u proxy. I recommend the [bubuntux/nordvpn](https://github.com/bubuntux/nordlynx) docker image to be run alongside this.

When the app first loads, it will prefix all URLs in the m3u file with the proxy endpoint.
For example, see the lines below in a sample m3u file:

```
#EXTM3U url-tvg="http://url-to-epg.com/epg"
#EXTINF:-1 tvg-id="mlbnet.us" tvg-name="US MLB Network (S)" tvg-logo="" group-title="MLB",US MLB Network (S)
https://url-to-mlb-network-stream.com/stream/
```

Assuming you don't use nginx and bind to port 8080, this will be replaced to:

```
#EXTM3U url-tvg="http://your-local-ip-address:8080/proxy/data/http://url-to-epg.com/epg"
#EXTINF:-1 tvg-id="mlbnet.us" tvg-name="US MLB Network (S)" tvg-logo="" group-title="MLB",US MLB Network (S)
http://your-local-ip-address:8080/proxy/stream/https://url-to-mlb-network-stream.com/stream/
```

Then instead of pointing your IPTV player to the original m3u file, you will set up your IPTV player to point to:

http://your-local-ip-address:8080/static/iptv.m3u

This will route all IPTV traffic to go accross a VPN, which can be helpful if your TV doesn't support VPN configurations.

## Docker Compose

```
version: '3'

services:
  nordlynx:
    image: ghcr.io/bubuntux/nordlynx
    network_mode: bridge
    cap_add:
      - NET_ADMIN
    environment:
      - PRIVATE_KEY=[See bubuntux/nordvpn docs]
      - PUID=1000
      - PGID=1000
      - ALLOWED_IPS=0.0.0.0/0
      - NET_LOCAL=[See bubuntux/nordvpn docs]
      - QUERY=filters\[country_id\]=228&filters\[servers_groups\]\[identifier\]=legacy_p2p
    ports:
      - 8080:8080
      - 80:80
    restart: unless-stopped

  iptv_proxy:
    image: parkerr1992/iptv-proxy
    container_name: iptv_proxy
    restart: unless-stopped
    network_mode: service:nordlynx
    environment:
      - M3U_LOCATION= # Required. Either a path or URL.
      - RELOAD_INTERVAL_MIN=60 # Not required and defaults to 60. This is used to update the /static directory with the latest m3u file.
      - LISTEN_PORT=8080
      - M3U_PORT=8080 # The port to add to the m3u file. If the app is running on port 80, you may not need this.

    depends_on:
      - nordlynx
```

### Configuration / Environment variables
| Name | Use | Example |
|--|--|--|
| M3U_LOCATION | File path or URL to the M3U | https://tv.myprovider.com:80/get.php?username=myUsername&password=myPassword&type=mpegts&output=m3u_plus |
| XMLTV_LOCATION | Optional file path or URL to an XMLTV file | https://tv.myprovider.com:80/xmltv.php?username=myUsername&password=myPassword |
| M3U_PORT | The port that will be written to your proxified M3U + XMLTV | 443 |
| M3U_HOST | The hostname that will be written to your proxified M3U + XMLTV | iptv-proxy.mydomain.lan |
| LISTEN_PORT | The port the process will really listen on | 8080 |
| USE_HTTPS | Will use https as URI scheme for references to the proxy | True |
| RELOAD_INTERVAL_MIN | The interval in minutes in which the M3u + XMLTV gets re-fetched | 60 |
| GROUPS_FILTER | Optional comma-separated list of group-id's to filter out ('group-title="<groupname>"' in the '#EXTINF:' line) | \|MULTI\| NETFLIX,DE\| ALLGEMEIN,to check

### M3U Editor

To edit m3u files, I recommend [m3u4u](http://m3u4u.com). After editing the m3u file, you can point the `M3U_LOCATION` variable to the m3u4u output URL.
