from collections import OrderedDict
import struct

class CStructMeta(type):

    @classmethod
    def __prepare__(metacls, name, bases):
        return OrderedDict()

    def __new__(cls, name, parents, dct):
        if not dct['__module__'] == __name__:
            params = []
            struct_format = ''

            for key, value in dct.items():
                if key != '__module__':
                    params.append(key)
                    struct_format += value
                    del dct[key]

            def init(self, *args):
                if len(args) == 0:
                    for param in params:
                        self.__dict__[param] = None

                    return

                if len(args) != len(params):
                    raise TypeError('__init__() takes exactly %d arguments (%d given)' %
                            (len(params), len(args)))
                    
                for param, arg in zip(params, args):
                    self.__dict__[param] = arg

            dct['__init__'] = init

            def getattr_m(self, val):
                if val in params:
                    return self.__dict__[val]
                else:
                    raise ValueError()

            dct['__getattr__'] = getattr_m

            def setattr_m(self, key, value):
                if key in params:
                    return super(self.__class__, self).__setattr__(key, value)
                else:
                    raise ValueError('Member "%s" not in struct' % key)

            dct['__setattr__'] = setattr_m

            def pack(self):
                for param in params:
                    if self.__getattr__(param) is None:
                        raise ValueError('Struct member %s uninitialized' % param)

                return struct.pack(struct_format, *[self.__getattr__(p) for p in params])

            dct['pack'] = pack

            @classmethod
            def unpack(cls, bstring):
                values = struct.unpack(struct_format, bstring)
                s = cls(*values)
                return s

            dct['unpack'] = unpack

        return super(CStructMeta, cls).__new__(cls, name, parents, dct)

    def __init__(self, name, bases, attrs):
        super(CStructMeta, self).__init__(name, bases, attrs)

class CStruct(metaclass = CStructMeta):
    pass

