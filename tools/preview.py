#!/usr/bin/env python3
"""Build and serve only the generated public files on the local computer."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
import argparse, threading, webbrowser, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]

def snapshot():
    files=[p for folder in ['content','theme'] for p in sorted((ROOT/folder).rglob('*')) if p.is_file()]
    files.append(ROOT/'tools/build.py')
    return tuple((str(p),p.stat().st_mtime_ns) for p in files)

def main():
    parser=argparse.ArgumentParser(description='ISAB local preview; no login, no upload.')
    parser.add_argument('--port',type=int,default=8926)
    parser.add_argument('--no-browser',action='store_true')
    args=parser.parse_args()
    def build():subprocess.run([sys.executable,str(ROOT/'tools/build.py')],cwd=ROOT,check=True)
    build()
    class Handler(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Cache-Control','no-store');super().end_headers()
        def log_message(self,*args): pass
    # Only dist is exposed; manuscripts and handover documents stay outside the server.
    server=None
    for port in range(args.port,args.port+20):
        try:
            server=ThreadingHTTPServer(('127.0.0.1',port),partial(Handler,directory=str(ROOT/'dist')));break
        except OSError as exc:
            if exc.errno not in (48,98):raise
    if server is None:raise RuntimeError('No free preview port. Close an earlier preview and try again.')
    stopped=threading.Event()
    def watch():
        state=snapshot()
        while not stopped.wait(1):
            current=snapshot()
            if current==state:continue
            state=current
            try:build();print('文稿已更新，请刷新网页。 / Updated. Refresh the browser.',flush=True)
            except Exception as exc:print('文稿有一处需要修正；上一版预览仍保留。 / Check:',exc,flush=True)
    threading.Thread(target=watch,daemon=True).start()
    url=f'http://127.0.0.1:{server.server_port}/'
    print('\n本地预览 / Local preview: '+url+'\n保存文稿后刷新网页。关闭此窗口或按 Control+C 结束。\n',flush=True)
    if not args.no_browser:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:stopped.set();server.server_close()

if __name__=='__main__':main()
