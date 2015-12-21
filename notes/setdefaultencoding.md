fix bugs in setuptools

edit the $PYPATH\Lib\mimetypes.py

if sys.getdefaultencoding()!='gbk':
   reload(sys)
   sys.setdefaultencoding('gbk')