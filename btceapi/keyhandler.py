# Copyright (c) 2013 Alan McIntyre

import warnings


class KeyData(object):
    def __init__(self, secret, nonce):
        self.secret = secret
        self.nonce = nonce


class KeyHandler(object):
    '''KeyHandler handles the tedious task of managing nonces associated
    with a BTC-e API key/secret pair.
    The getNextNonce method is threadsafe, all others are not.'''
    def __init__(self, filename=None, resaveOnDeletion=True):
        '''The given file is assumed to be a text file with three lines
        (key, secret, nonce) per entry.'''
        if not resaveOnDeletion:
            warnings.warn("The resaveOnDeletion argument to KeyHandler will"
                          " default to True in future versions.")
        self._keys = {}
        self.resaveOnDeletion = False
        self.filename = filename
        if filename is not None:
            self.resaveOnDeletion = resaveOnDeletion
            f = open(filename, "rt")
            while True:
                key = f.readline().strip()
                if not key:
                    break
                secret = f.readline().strip()
                nonce = int(f.readline().strip())
                self.addKey(key, secret, nonce)

    def __del__(self):
        self.close()

    def close(self):
        if self.resaveOnDeletion:
            self.save(self.filename)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @property
    def keys(self):
        return self._keys.keys()

    def getKeys(self):
        return self._keys.keys()

    def save(self, filename):
        f = open(filename, "wt")
        for k, data in self._keys.items():
            f.write("%s\n%s\n%d\n" % (k, data.secret, data.nonce))

    def addKey(self, key, secret, next_nonce):
        self._keys[key] = KeyData(secret, next_nonce)

    def getNextNonce(self, key):
        data = self._keys.get(key)
        if data is None:
            raise Exception("Key not found: %r" % key)

        nonce = data.nonce
        data.nonce += 1

        return nonce

    def getSecret(self, key):
        data = self._keys.get(key)
        if data is None:
            raise Exception("Key not found: %r" % key)

        return data.secret

    def setNextNonce(self, key, next_nonce):
        data = self._keys.get(key)
        if data is None:
            raise Exception("Key not found: %r" % key)
        data.nonce = next_nonce
