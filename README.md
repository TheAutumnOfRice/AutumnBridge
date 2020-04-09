# AutumnBridge 1.0.1
An easy, convenient and fast tool to transfer data (especially numpy type) between python and matlab.
Based on scipy.io. All the transmission based on hard disk IO and it is not as fast as memory transmission, but much faster than the original matlab.double(ndarray.tolist())
User should install matlab and its python engine first.

## Why use AutumnBridge
* AutumnBridge supports numpy type data, so it is very convenient to transfer data between python and Matlab.
* AutumnBridge has easy one-word method `E`,`R`,`A`,`S` to simplify usage.
* Based on scipy.io, AutumnBridge transfer data using `.mat` files so that it can handle almost every type of data and the transmission speed is much faster than the original API.
* AutumnBridge can wrap any Matlab function without change the program. It will create a 'Bridge' .m file that covers all the preparation works like `load` and `save`.

## Install
1. Check your Matlab version and python version. Lower version Matlab may not be compatible with high-version python. See: https://ww2.mathworks.cn/help/matlab/matlab_external/system-and-configuration-requirements.html
2. Install Matlab Engine for python. Check the website:https://ww2.mathworks.cn/help/matlab/matlab_external/install-the-matlab-engine-for-python.html?lang=en 
3. Download this project.
4. Use `python setup.py install` to install this project.
## Sample 1: Use AutumnBridge
```python
from AutumnBridge import AutumnBridge
# Start MATLAB 2019a before using AutumnBridge
AB = AutumnBridge(connect=True)
# You can start a new matlab by using connect=False
```
## Sample 2: Run Matlab Code with AutumnBridge
```python
from AutumnBridge import AutumnBridge
AB = AutumnBridge(connect=True)
# Execute one matlab command without return values
AB.E('x=ones(5,5);')
AB.E('y=magic(5);')
# Execute one matlab command with return values 
S=AB.R('x+y')
#S=
#array([[18, 25,  2,  9, 16],
#       [24,  6,  8, 15, 17],
#       [ 5,  7, 14, 21, 23],
#       [11, 13, 20, 22,  4],
#       [12, 19, 26,  3, 10]], dtype=uint8)

# Get shape(size) of one matlab variable
print(AB.S('x'))
# (5, 5)

# Get all the variable names
ALL=AB.A()
# ALL=array(['x', 'y'], dtype=object)
# Iterate all the matlab variables
for i in AB:
    print(i)
# x
# y

# Show all the variables
AB.show()
#  Name      Size            Bytes  Class     Attributes
#  x         5x5               200  double              
#  y         5x5               200  double             
```
## Sample 3: Workspace Tricks
```python
from AutumnBridge import AutumnBridge
import numpy as np
AB=AutumnBridge(connect=True)
AB['a']=np.array([[1,2],[3,4]])
AB['b']=np.ones((2,2))
AB.E('c=a.*b;')
c=AB['c']
print(c)
# array([[1, 2],
#        [3, 4]], dtype=uint8)
print('b' in AB)
# True
```
## Sample 4: Transfer Large Data
```python
from AutumnBridge import AutumnBridge
import numpy as np
from time import time
AB = AutumnBridge(connect=True)
t=time()
AB['A']=np.random.rand(1000,1000)
L,U,P=AB.R('lu(A)',nargout=3)
print(time()-t)
# 0.6980011463165283
```
## Sample 5: Use Matlab Wrapper
If you have written a Matlab function, and now you'd like to use it in python, the Matlab wrapper will help you.
Your m file (example) `Hello.m`:
```matlab
function [a,b]=Hello(x1,x2,x3)
    a=min([x1,x2,x3]);
    b=max([x1,x2,x3]);
end
```
```python
from AutumnBridge import AutumnBridge
AB = AutumnBridge(connect=True)
a,b=AB('Hello',3,4,5,nargout=2)
print(a,b)
# 3 5
```

## Sample 6: Wrap One Matlab Function Many Times
```python
from AutumnBridge import AutumnBridge,RandomBridge
from math import sin,cos,tan
AB = AutumnBridge(connect=True)
RB = RandomBridge()
# Make a bridge manually, avoiding recreating the same bridge many times.
AB.BuildBridge('Hello',RB,3,2)
for i in range(50):
    a,b=AB('Hello',sin(i),cos(i),tan(i),nargout=2,bridge=RB,NewBridge=False)
AB.DelBridge('Hello') # Manually Delete Bridge Files
```
## Sample 7: Original Matlab API
AB.XXX is equal to the original eng.XXX
In this way, data are transfered in original form. It may be faster at small data, but can be extreamly slow in medium scaled data.
```python
from AutumnBridge import AutumnBridge
AB = AutumnBridge(connect=True)
X=AB.eng.eval('[2,3,4]',nargout=1)
# matlab.double([[2.0,3.0,4.0]])
```

## Note:
* Currently, AutumnBridge can only transfer `char` ,`double` or `complex` type in Matlab (can be in the form of struct, cell or matrix). Other types like `sym`, `string`, `figure`, and matlab `class` objects are not supported.
* The wrapper method is recommended because it's still takes time to call Matlab instructions in python. Both python and matlab are so powerful that can handle most of the tasks. Merge python and matlab programs only when necessary. 
