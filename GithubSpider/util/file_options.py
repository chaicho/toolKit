import os
import shutil
def move_file(old_path, new_path):

    filelist = os.listdir(old_path)  # 列出该目录下的所有文件,listdir返回的文件列表是不包含路径的。
    for file in filelist:
        src = os.path.join(old_path, file)
        dst = os.path.join(new_path, file)
        print('src:', src)
        print('dst:', dst)
        shutil.move(src, dst)


def rmdir(dir):
    # 判断是否是文件夹，如果是，递归调用rmdir()函数
    if(os.path.isdir(dir)):
        # 遍历地址下的所有文件及文件夹
        for file in os.listdir(dir):
            # 进入下一个文件夹中进行删除
            rmdir(os.path.join(dir, file))
        # 如果是空文件夹，直接删除
        if (os.path.exists(dir)):
            os.rmdir(dir)
    # 如果是文件，直接删除
    else:
        if(os.path.exists(dir)):
            os.remove(dir)
