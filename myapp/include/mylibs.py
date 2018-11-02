# -*- coding: UTF-8 -*-
#类定义
import  os
class MyLibs_logs:
    cpath=''
    cname=''
    def __init__(self,mycpath,mycname):
        self.cpath=mycpath
        self.cname=mycname

    def log_write(self,str):
      curentpath_file = self.cpath + self.cname
      if os.path.isfile(curentpath_file):
         file=open(curentpath_file,'a')
         file.write(str)
      else:
         file=open(curentpath_file,'w')
         file.write(str)
