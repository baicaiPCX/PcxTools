import os
import glob
import shutil
import argparse

dirSrcV="DIRSRC"
dirDstV="DIRDST"

dirSrc="."
dirDst="."

if dirSrcV in os.environ:
    dirSrc=os.environ[dirSrcV]
if dirDstV in os.environ:
    dirDst=os.environ[dirDstV]

print(f"{dirSrcV}:{dirSrc}")
print(f"{dirDstV}:{dirDst}")
print('''
Set DIRSRC and DIRDST on powershell:
$env:DIRSRC="./"
$env:DIRDST="./
''')


def rename_basename(basename,newname):
    bn_split=basename.split(".")
    nname=newname.replace("*",bn_split[0])
    if "." not in newname:
        nname=basename.replace(bn_split[0],nname)
    return nname

def rename_path(path,baseNewName):
    basename=os.path.basename(path)
    nBasename=rename_basename(basename,baseNewName)
    dir_=os.path.dirname(path)
    return os.path.join(dir_,nBasename)

def back_basename(basename,newname):
    nname_split=newname.split("*")
    bBack=True
    for subn in nname_split:# 检测是否完全匹配
        bBack=bBack and (subn in basename)
    if not bBack:
        print(f"Error:{basename} not match {newname},can't back.")
        return basename
    for subn in nname_split:
        basename=basename.replace(subn,"")
    return basename

def back_path(path,baseNewName):
    basename = os.path.basename(path)
    nBasename = back_basename(basename, baseNewName)
    dir_ = os.path.dirname(path)
    return os.path.join(dir_, nBasename)

def rename(src,dst):
    if os.path.exists(dst) and (not os.path.samefile(src,dst)):# 判断存在并且不同文件
        os.remove(dst)
        print(f"Deleted {dst}")
    os.rename(src, dst)
    print(f"Rename {src} to {dst}")

def copyfile(src,dst):
    if os.path.exists(dst) and (not os.path.samefile(src,dst)):
        os.remove(dst)
        print(f"Deleted {dst}")
    shutil.copy(src,dst)
    print(f"Copy {src} to {dst}")
##############################################################

def main_copy(names,dst_names,rb_names):
    files=glob.glob(os.path.join(dirSrc,names))
    if len(files)<1:
        print(f"{dirSrc}:has no files {names}")
        return
    for index,path in enumerate(files):
        print(f"**************** {index} ****************")
        basename=os.path.basename(path)
        dstPath=os.path.join(dirDst,basename)
        dstPath = rename_path(dstPath, dst_names)
        if os.path.exists(dstPath): # 对旧的文件重命名
            nPathb=rename_path(dstPath,rb_names)
            rename(dstPath,nPathb)

        copyfile(path,dstPath)

def main_back(names,dst_names,rb_names):
    files=glob.glob(os.path.join(dirDst,names))
    for index,path in enumerate(files):
        print(f"**************** {index} ****************")
        dstPath=back_path(path,dst_names)
        if os.path.exists(dstPath):
            rbPath = rename_path(dstPath, rb_names)
            rename(dstPath,rbPath)

        rename(path,dstPath)

def main_list(names):
    files = glob.glob(os.path.join(dirDst, names))
    for index, path in enumerate(files):
        print(f"{index}:{path}")

def main_remove(names):
    files = glob.glob(os.path.join(dirDst, names))
    for index, path in enumerate(files):
        os.remove(path)
        print(f"{index}:{path}")

def main_rename(names,dst_names):
    files = glob.glob(os.path.join(dirDst, names))
    for index, path in enumerate(files):
        print(f"**************** {index} ****************")
        pathn=rename_path(path,dst_names)
        rename(path,pathn)

if __name__ == "__main__":
     parse=argparse.ArgumentParser()
     parse.add_argument("-c",help="copy", action="store_true")
     parse.add_argument("-b",help="back", action="store_true")
     parse.add_argument("-l",help="list", action="store_true")
     parse.add_argument("-rm",help="remove dst file",action="store_true")
     parse.add_argument("-rn",help="rename dst file",action="store_true")
     parse.add_argument("names",type=str,help="file names.")
     parse.add_argument("-d",type=str,default="*",help="dst names")
     parse.add_argument("-rb",type=str,default="*",help="rename old file before operation.")
     args=parse.parse_args()
     print("names:",args.names)
     print("-d:",args.d)
     print("-c:",args.c)
     print("-b:",args.b)
     print("-l:",args.l)
     print("-rb:",args.rb)
     print("-rm:",args.rm)
     print("-rn:",args.rn)

     if args.c:
         print("Operate:Copy.")
         main_copy(args.names,args.d,args.rb)

     if args.b:
        print("Operate:Back.")
        main_back(args.names,args.d,args.rb)

     if args.l:
        print("Operate:List.")
        main_list(args.names)

     if args.rm:
         print("Operate:Remove.")
         main_remove(args.names)

     if args.rn:
         print("Operate:Rename.")
         main_rename(args.names,args.d)

     print("Finished.")