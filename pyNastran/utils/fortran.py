from numpy import ones


class OneBasedArray(object):
    def __init__(self, Array):
        self.data = Array
        self.shape = self.data.shape
        self.ndim = self.data.ndim

    def __getitem__(self, key):
        #print "key_get =", str(key)
        key0 = self.__update_key(key, 0)
        key1 = key[1]
        key = (key0, key1)
        #print "key_get", key
        #print "---"
        return self.data[key0, key1]

    def __update_key(self, key, id):
        if isinstance(key, int):
            return key - 1
        key_id = key[id]
        if isinstance(key_id, int):
            key_id = key_id - 1
        elif not (key[id].start is None and key_id.stop is None and key_id.step is None):
            key_id = key_id - 1
        else:
            key_id = key_id
        return key_id

    def __setitem__(self, key, value):
        print "key_set1 =", str(key)
        key2 = []

        for i in xrange(self.ndim):
            ikey = self.__update_key(key, i)
            key2.append(ikey)
        key2 = tuple(key2)
        #print "key_set2", key2
        #print "value_set =", value - 1
        #print "---"
        self.data[key2] = value# - 1

    def __repr__(self):
        return str(self.data)

if __name__ == '__main__':
    a = OneBasedArray(ones((3, 3), 'i'))
    print a

    a[1,1] = 5
    print a

    a[2,:] = 10
    print a

    b = OneBasedArray(ones(3, 'i'))
    print b
    b[3] = 5
    print b