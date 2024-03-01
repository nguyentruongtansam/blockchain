This project is run and tested on Python 3.10.12.

Please install these packages before running the Blockchain:

```
$ pip install requests
$ pip install flask
```

How to run Blockchain server:

```
$ cd <[blockchain_with_merkle_tree] or [blockchain_without_merkle_tree]>
$ python blockchain_server.py -p 8000
```

View Blockchain:

```
$ python blockchain_cli.py --server http://localhost --port 8000 --view
```

Add Transaction:

```
$ python blockchain_cli.py --server http://localhost --port 8000 --add '{"sender": "Alice", "receiver": "Bob", "amount": 50}'
```

Mine Block

```
$ python blockchain_cli.py --server http://localhost --port 8000 --mine
```

Verify Transaction

```
$ python blockchain_cli.py --server http://localhost --port 8000 --verify '{"sender": "Alice", "receiver": "Bob", "amount": 50}'
```

Validate Chain:

```
$ python blockchain_cli.py --server http://localhost --port 8000 --validate
```