from matlab.engine import start_matlab, connect_matlab
from typing import Optional
from scipy.io import savemat, loadmat
import numpy as np
from os import remove
from os.path import exists
from os import getcwd


def RandomBridge():
    return 'B' + str(np.random.randint(1000000, 9999999))


def _MakeArgs(num: int, sym: str,br:str=''):
    """
    Input Num, Return Args Name list like [a1,a2,...,an]
    """
    return ['%s%s%d' % (sym,br,i) for i in range(num)]


def _Del(fname: str):
    if exists(fname):
        remove(fname)


class AutumnBridge:
    def __init__(self, connect=False, desktop=False, background=False, MoreOpt=None,ID=None):
        """
        Initialize the bridge between python and matlab.
        :param connect: bool
            If True, AutumnBridge will connect to an opened Matlab.
            Otherwise, AutumnBridge will start a new Matlab.
        :param desktop: bool
            Avaliable only when connect==False
            If True, Matlab will be start in desktop mode.
        :param background: bool
            Avaliable only when connect==False
            If True, Matlab will start in async mode.
        :param MoreOpt: str = None
            Avaliable only when connect==False
            More parameters avaliable in Matlab Options.
        :param ID: int
            The ID of the bridge.
            If None, the ID will be id(self).
        """
        opt = '-desktop' if desktop else '-nodesktop'
        self._floatformat=np.float64
        self._connect = connect
        self._ID = ID if ID is not None else id(self)
        if MoreOpt is not None:
            opt = opt + ' ' + MoreOpt
        self.eng = connect_matlab() if connect \
            else start_matlab(opt, background=background)
        self.eng.cd(getcwd())

    def __del__(self):
        """
        Quit Matlab.
        """
        if self._connect is False:
            self.eng.quit()

    """ Dispatched
    def __getattr__(self, item):
        '''
        The same function as eng.__getattr__
        '''
        return self.eng.__getattr__(item)
    """
    def E(self, command: str, nargout=0):
        """
        A fast eval method.
        :param command: str
            matlab command.
        :param nargout: int
            Number of output arguments.
        :return:
            Output arguments
        """
        try:
            return self.eng.eval(command, nargout=nargout)
        except Exception as e:
            raise e

    def R(self, command: str, nargout=1):
        """
        A fast eval method, but return with scipy.io.
        It can return big matrix.
        :param command: str
            matlab command.
        :param nargout: int
            Number of output arguments.
        :return:
            Output arguments
        """
        BR = RandomBridge()
        ArgOuts = _MakeArgs(nargout, 'Out',BR)
        fname = self._BridgeName(BR, '_out.mat')
        try:
            self.E('[%s]=%s;' % (','.join(ArgOuts), command))
            self.E('save %s %s' % (fname, ' '.join(ArgOuts)))
            self.E('clear %s' % ' '.join(ArgOuts))
            P = self._FromMat(BR, nargout)
            self._DelInOut(BR)
            if len(P)==1:
                return P[0]
            else:
                return P
        except Exception as e:
            self._DelInOut(BR)
            raise e

    def __getitem__(self, item: str):
        """
        Get an item from workspace
        :param item: str
            Variable.
        """
        if self.__contains__(item):
            # item exist.
            RB = RandomBridge()
            fname = self._BridgeName(RB, '_out.mat')
            self.E('save %s %s' % (fname, item))
            P = self._FromMat(RB, 1,[item])
            self._DelInOut(RB)
            if len(P)==1:
                return P[0]
            else:
                return P
        else:
            raise KeyError(item)

    def __setitem__(self, item: str, value):
        """
        Set an item into workspace
        :param item: str
            Variable
        :param value:
            any value to set to variable.
        """
        RB = RandomBridge()
        self._ToMat(RB, value, argname=[item])
        fname = self._BridgeName(RB, '_in.mat')
        self.E('load %s' % fname)
        self._DelInOut(RB)

    def __contains__(self, item):
        """
        Check if item in workspace
        :param item: str
            Variable
        :return: bool
            True if workspace contains item
        """
        return self.E("exist('%s')" % item, 1) == 1
    def __iter__(self):
        A = self.A()
        for i in A:
            yield i

    def S(self, item):
        """
        Show the shape / size of an item
        :param item: str
            Variable
        :return: tuple
            shape or size
        """
        if not self.__contains__(item):
            raise KeyError(item)
        return tuple(self.R('size(%s)' % item))
    def A(self):
        """
        Get all the variables' names.
        :return:
        names of the variables
        """
        try:
            return self.R('whos()')['name']
        except IndexError:
            return np.array([])
    def show(self):
        """
        Equals to E('whos')
        """
        self.E('whos')
    def _BridgeName(self, bridge: str, suf: str):
        """
        Return The Name Of the Bridge File
        """
        return "AutumnBridge_%s_%s%s" % (str(self._ID), str(bridge), suf)

    def BuildBridge(self, func: str, bridge: str, nargin: int, nargout: int):
        """
        Build .m Bridge.
        :param func: str
            Name of the function that will be wrapped.
        :param bridge: str
            Name of the bridge
        :param nargin: int
            Number of input arguments
        :param nargout: int
            Number of output arguments
        """
        fname = self._BridgeName(bridge, '.m')
        funname = self._BridgeName(bridge, '')
        inmatname = self._BridgeName(bridge, '_in.mat')
        outmatname = self._BridgeName(bridge, '_out.mat')
        OutArgs = _MakeArgs(nargout, 'Out',bridge)
        InArgs = _MakeArgs(nargin, 'In',bridge)
        with open(fname, 'w') as f:
            P = []
            P += ['function []=%s()\n' % funname]
            P += ['\tload %s\n' % inmatname]
            P += ['\t[%s]=%s(%s);\n' % (','.join(OutArgs), func, ','.join(InArgs))]
            P += ['\tsave %s %s\n' % (outmatname, ' '.join(OutArgs))]
            P += ['end\n']
            f.writelines(P)

    def DelBridge(self, bridge: str):
        """
        Delete Bridge file.
        :param bridge: str
            The name of bridge
        :return:
        """
        fname = self._BridgeName(bridge, '.m')
        _Del(fname)

    def _DelInOut(self, bridge: str):
        inmatname = self._BridgeName(bridge, '_in.mat')
        outmatname = self._BridgeName(bridge, '_out.mat')
        _Del(inmatname)
        _Del(outmatname)

    def _ToMat(self, bridge: str, *argin, argname=None):
        inmatname = self._BridgeName(bridge, '_in.mat')
        if argname is None:
            InArgs = _MakeArgs(len(argin), 'In',bridge)
        else:
            InArgs = argname
        argin=list(argin)
        for i,j in enumerate(argin):
            if type(argin[i]) is int:
                argin[i]=float(argin[i])
            if type(j) in [list,tuple]:
                argin[i]=np.array(j)
            if type(argin[i]) is np.ndarray and 'int' in argin[i].dtype.name:
                argin[i]=argin[i].astype(self._floatformat)

        savemat(inmatname, dict(zip(InArgs, argin)))

    def _FromMat(self, bridge: str, nargout: int,argname=None):
        outmatname = self._BridgeName(bridge, '_out.mat')
        if argname is None:
            OutArgs = _MakeArgs(nargout, 'Out',bridge)
        else:
            OutArgs=argname
        D = loadmat(outmatname,squeeze_me=True,struct_as_record=True)
        L = []
        for i in OutArgs:
            L = L + [D[i]]
        return tuple(L)

    def __call__(self, func: str, *argin, nargout=1, bridge: Optional[str] = None, NewBridge='auto', delete='auto'):
        """
        Wrap a matlab function with Bridge, and transfer data/parameters much more faster
        using scipy.io.
        :param func: str
            the function to be wrapped
        :param argin: Any type that can be recognized by scipy.io.savemat
            arguments or data that will be transfered to the matlab function
        :param nargout: int
            The number of output arguments
        :param bridge: str
            The name of bridge.
            If None: the name will be random int.
        :param NewBridge: bool or 'auto'
            If True, the bridge .m file will be create anyhow.
            If False, the bridge .m file will not be created, and make sure
                you have ever created one with certain ID and Bridge name.
            If 'auto', the bridge .m file will be create if there doesn't
                exist one.
        :param delete: bool or 'auto'
            If True, the bridge .m file will be delete after function calling.
            If False, the bridge .m file will not be delete.
            If 'auto', delete=True if bridge is not None.
        :return:
            Tuple(arg0,arg1,...,argn), n=nargout
        """
        if delete == 'auto':
            delete = bridge is not None
        else:
            assert type(delete) is bool
        if bridge is None:
            bridge = RandomBridge()
        fname = self._BridgeName(bridge, '.m')
        funname = self._BridgeName(bridge, '')
        if NewBridge == 'auto':
            NewBridge = not exists(fname)
        else:
            assert type(NewBridge) is bool
        if NewBridge:
            self.BuildBridge(func, bridge, len(argin), nargout)
        try:
            self._ToMat(bridge, *argin)
            self.eng.__getattr__(funname)(nargout=0)
            T = self._FromMat(bridge, nargout)
            self._DelInOut(bridge)
            if delete:
                self.DelBridge(bridge)
        except Exception as e:
            if delete:
                self.DelBridge(bridge)
            self._DelInOut(bridge)
            raise e
        if len(T) == 1:
            return T[0]
        else:
            return T

