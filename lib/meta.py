# coding=utf-8
import traceback
import types

from decorator import decorator
from meta_wrapper import MetaWrapper


@decorator
def runBaseThenInh(fun, baseFun=None, *args, **kwargs):
    baseFun(*args, **kwargs)
    return fun(*args, **kwargs)


@decorator
def runInhThenBase(fun, baseFun=None, *args, **kwargs):
    v = fun(*args, **kwargs)
    baseFun(*args, **kwargs)
    return v


@decorator
def runInhWhenBaseReturnTrue(fun, baseFun=None, *args, **kwargs):
    stateOk = baseFun(*args, **kwargs)
    if stateOk:
        return fun(*args, **kwargs)


@decorator
def runBaseWhenInhReturnTrue(fun, baseFun=None, *args, **kwargs):
    stateOk = fun(*args, **kwargs)
    if stateOk:
        baseFun(*args, **kwargs)
    return stateOk


@decorator
def convertExceptionToString(fun, *args, **kwargs):
    try:
        return fun(*args, **kwargs)
    except Exception as exp:
        return '{}\n\n{}'.format(exp, traceback.format_exc()).replace('\n', '<br>\n')


class MetaBaseClassDecorator(MetaWrapper):
    OVERRIDE_ATTR = '__override__'

    @staticmethod
    def decorate(*controlFunctions):
        """Utility function to add decorator to function '__override__' attribute"""
        def _decorate(decoratedFun):
            dec = getattr(decoratedFun, MetaBaseClassDecorator.OVERRIDE_ATTR, [])
            dec.extend(controlFunctions)
            setattr(decoratedFun, MetaBaseClassDecorator.OVERRIDE_ATTR, dec)
            return decoratedFun

        return _decorate

    def __new__(mcs, name, bases, namespace):
        """If function in base class has in '__override__' attribute any decorators,
        metaclass applies those decorators to inherited function"""
        for funName, inhFun, baseFun in mcs._baseFunctionIterator(bases, namespace):
            decFunctions = getattr(
                baseFun, MetaBaseClassDecorator.OVERRIDE_ATTR, [])
            if decFunctions:
                for decFunction in decFunctions:
                    try:
                        inhFun = decFunction(baseFun=baseFun)(inhFun)
                    except TypeError:
                        inhFun = decFunction(inhFun)

                namespace[funName] = mcs.decorate(*decFunctions)(inhFun)

        return super(MetaBaseClassDecorator, mcs).__new__(mcs, name, bases, namespace)

    @staticmethod
    def _baseFunctionIterator(bases, namespace):
        """yields tuple:
            - function name
            - original function in base class
            - override function in inherited class
        """
        for funName, inhFun in namespace.items():
            if isinstance(inhFun, types.FunctionType):
                for base in bases:  # type: object
                    baseFun = getattr(base, funName, None)
                    if baseFun:
                        yield funName, inhFun, baseFun
                        break
