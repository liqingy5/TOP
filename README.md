# Together Old & Pet (TOP)
## Installation
Install the project under Linux/MacOS environment
### Create virtual environment if not created
```console
$ python3 -m venv env
```

### Activate virtual environment
```console
$ . env/bin/activate
```

### Install requirement packages
```console
$ pip install -r requirements.txt
```

### Initial database
```console
$ flask initdb
```

### Drop and re-inital database
```console
$ flask initdb --drop
```

### Add hardcoded information to database table
```console
$ flask forge
```

### Run the application
```console
$ flask run
```

## Other Useful command

### Deactivate virtual environment
```console
$ deactivate
```

### ((only use when new packages are added)) Get all the packages along with dependencies in requirements.txt 
```console
$ pip freeze > requirements.txt
```


## Other useful resource
[Flask 入门教程](https://tutorial.helloflask.com/form/)

