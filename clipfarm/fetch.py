"""Stream authorized direct HTTP(S) video files without holding them in RAM.

No social-site scraping, DRM bypass, cookie collection, or login automation.
"""
import ipaddress
import os
import socket
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

class GuardedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        validate_url(newurl)
        return super().redirect_request(req,fp,code,msg,headers,newurl)


def validate_url(url):
    info=urlparse(url)
    if info.scheme not in {'https','http'} or not info.hostname or info.username or info.password:
        raise ValueError('Only direct public HTTP(S) links are supported')
    try:
        ips=socket.getaddrinfo(info.hostname,info.port or (443 if info.scheme=='https' else 80),type=socket.SOCK_STREAM)
    except OSError as e:
        raise ValueError(f'Unable to resolve host: {e}') from e
    if any(not ipaddress.ip_address(record[4][0]).is_global for record in ips):
        raise ValueError('Local/private host address blocked')


def fetch(url,dest,*,max_gb=10,assert_rights=False):
    if not assert_rights:
        raise PermissionError('Confirm you own or are licensed to download/transform this file: --rights-confirmed')
    validate_url(url)
    dest=Path(dest)
    dest.parent.mkdir(parents=True,exist_ok=True)
    part=dest.with_name(dest.name+'.part')
    existing=part.stat().st_size if part.exists() else 0
    request=urllib.request.Request(url,headers={'User-Agent':'CloudLabClipFarm/1.0',
        **({'Range':f'bytes={existing}-'} if existing else {})})
    opener=urllib.request.build_opener(GuardedRedirect())
    cap=int(max_gb*1_000_000_000)
    with opener.open(request,timeout=45) as response:
        status=response.status
        # If the server ignores Range, restart (do not accidentally append a duplicate file).
        if existing and status != 206:
            existing=0
        mode='ab' if existing and status==206 else 'wb'
        declared=response.headers.get('Content-Length')
        if declared and existing + int(declared) > cap:
            raise ValueError(f'Download exceeds configured {max_gb:g} GB limit')
        seen=existing
        with open(part,mode) as out:
            while True:
                chunk=response.read(4*1024*1024)
                if not chunk:
                    break
                seen+=len(chunk)
                if seen>cap:
                    raise ValueError(f'Download exceeded configured {max_gb:g} GB limit; partial kept for inspection')
                out.write(chunk)
    if not part.is_file() or part.stat().st_size == 0:
        raise ValueError('Empty download')
    os.replace(part,dest)
    return str(dest)
