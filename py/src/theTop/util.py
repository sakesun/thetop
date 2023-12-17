#! -*- coding: utf-8 -*-

def slotty(obj): return '__dict__' not in dir(obj)

def assert_slotty(cls):
    assert slotty(cls.__new__(cls)), \
           'The class "%s" is expected to be "slotted class"' % str(cls)

def local_filename(name, ref=None):
    import sys
    import os.path
    if ref is None: ref = local_filename
    mod = sys.modules[ref.__module__]
    (p,f) = os.path.split(mod.__file__)
    return os.path.join(p, name)

class propattr(object):
    def __init__(self, func): self.func = func
    def __get__(self, instance, owner):
        if instance is None: return self
        v = self.func(instance)
        instance.__dict__[self.func.__name__] = v
        return v

class NotFound(LookupError):
    '''An exception to be raised when expected lookup item is not found'''
    pass

class TooMany(LookupError):
    '''An exception to be raised when more items than expected are found'''
    pass

class MoreThanOne(TooMany):
    '''An exception to be raised when more than one item are found'''
    pass

class CannotModify(Exception):
    '''An exception to be raised when trying to modify some protected value'''
    pass

def get_single(values):
    i = iter(values)
    try:
        result = i.next()
    except StopIteration:
        raise NotFound()
    try:
        i.next()
    except StopIteration:
        return result
    raise MoreThanOne()

def assure_singularity(size):
    '''check the size and raise appropriate exception when size is not one as expected'''
    if size == 0: raise NotFound()
    if size > 1: raise MoreThanOne()

def SHOULD_NOT_REACH_HERE(msg=''):
    raise AssertionError('Should not reach here' + ((' >>> ' + msg) if msg else ''))
