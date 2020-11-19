# Secret Voldemort by Pyhterin, Backend

Secret Voldemort is a card game, now in pyhton.

## Installation
To be able to run our backend you will need to execute

```
pip3 install -r requirements.txt
```
## Usage
To start the server, go to `src/` and run:
```
uvicorn main:app
```
You can interact with the server using the [OPENapi](127.0.0.1/8000/docs)

If you wish to test the software, on the src folder, do:
```
$ python3 test_setup.py
$ pytest --cov=. test_*
```

If you want to see how a match is played, you can delete all the '#' on the 
test_game.py file, and run:
```
$ python3 test_setup.py
$ python3 test_game.py
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
