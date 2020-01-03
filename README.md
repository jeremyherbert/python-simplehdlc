# python-simplehdlc
A python implementation of the simplehdlc parser/encoder. More information about the packet structure can be found at [https://github.com/jeremyherbert/simplehdlc](https://github.com/jeremyherbert/simplehdlc).

Only python 3.6+ is supported.

License is MIT.

### Installing

You can install this package using `pip`:

`pip install simplehdlc`

or by cloning this git repository and running:

`python setup.py install`

### Usage

```python
from simplehdlc import SimpleHDLC

# note that encode is a class method
encoded = SimpleHDLC.encode(b'abcdefg')

def success_callback(payload: bytes):
    print("success:", payload)

hdlc = SimpleHDLC(success_callback, max_len=1024)
hdlc.parse(encoded)  # will print "success: b'abcdefg'" via the callback
```