# echout

数据外带平台

# 友好的日志界面

<img width="2301" height="1367" alt="image" src="https://github.com/user-attachments/assets/898b938d-d729-4cab-a18f-27c8b7ff60e4" />


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
