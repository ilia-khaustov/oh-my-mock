Oh My Mock
==========

 > Python 3.5+ required
 
About
-----

OhMyMock is a tool for testing web clients without a real HTTP server.

How to Install
--------------

In project directory:

    $ python setup.py install
    
After installing, `omm-server` shortcut is added to your PATH.

How to Use
----------

 > For formatting JSON a `jq` was used.
 
 >> Ubuntu: `apt install jq`
 
 >> MacOS: `brew install jq`
 
Run `omm-server` for given host/port:

    $ omm-server --host=localhost --port=4242
    
Create a mock for `GET /foo/bar` endpoint returning `foobar`:

    $ curl -X POST "http://localhost:4242/mock/get/foo/bar" -d "foobar"
    
Add another mock for the same endpoint returning error 500 twice:
    
    $ curl -X PUT "http://localhost:4242/mock/get/foo/bar?status=500&repeat=2" -d 'Ooops'
    
Now, test this:

    $ curl -v "http://localhost:4242/foo/bar"
    
View request <-- response history:

    $ curl "http://localhost:4242/mock/get/foo/bar" | jq

