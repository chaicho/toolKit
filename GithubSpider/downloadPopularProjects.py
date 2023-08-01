# -*- coding: UTF-8 -*-
import json
import ssl
import urllib
from urllib.request import Request, urlopen
import http.client
import time
import socket
import zipfile
import shutil
import os
import os
import datetime
import logging

from logger.loggerHelper import * 
from database.csvHelper import CsvProjectHelper
from util.file_options import *

unzipsDir = '/root/dependencySmell/evaluation/realProjects/projectsDir/'

zipsDir = '/root/dependencySmell/evaluation/realProjects/zipsDir/'

temp_unzips_dir = '/root/dependencySmell/evaluation/realProjects/tmpDir/'

max_crawling_single_time_num = 200  # max download zip_num

csv_helper = CsvProjectHelper(os.path.join('/root/dependencySmell/evaluation/realProjects/projectsInfo','projects.csv'))


def download_file(download_url, file_path):
    retries = 2
    while retries > 0:
        try:
            urllib.request.urlretrieve(download_url, file_path)
            logging.info("Download Success")
            return True
        except socket.timeout:
            retries -= 1
            if retries > 0:
                err_info = 'Reloading for %d time' % (
                    4 - retries) if retries == 1 else 'Reloading for %d times' % (4 - retries)
                logging.error(err_info)
                continue
            else:
                logging.error("downloading failed!")
                return False
        except Exception as e:
            retries -= 1
            logging.error(e)
            time.sleep(2)
            continue

def isSpringFrameWorkUsed(filename):
    if not os.path.isfile(filename):
        return False
    with open(filename, 'r') as pom_file:
        all_text = pom_file.read()
        if "spring" in all_text:
            return True
    return False

def filterProjects(projectName):
    '''judge if spring'''
    # print("judge if spring")
    unzip_folder = temp_unzips_dir + projectName + os.path.sep
    file_list=os.listdir(unzip_folder)
    project_root_dir = os.path.join(unzip_folder, file_list[0])
    pom_file_path = project_root_dir + os.path.sep + 'pom.xml'
    if not os.path.isfile(pom_file_path):
        logging.warn("no pom: "+pom_file_path)
        return False
    is_spring = isSpringFrameWorkUsed(pom_file_path)
    if is_spring:
        os.remove(zipsDir + projectName + '.zip')
        print("rm -r " + temp_unzips_dir + projectName)
        os.system("rm -r " + temp_unzips_dir + projectName)
        logging.error("spring project: "+projectName)
        return False
    '''计算test数目'''
    print("calculate test num")
    test_num_whole_proj = countTestNum(temp_unzips_dir + projectName)
    print("test num" + ":" + str(test_num_whole_proj))
    if test_num_whole_proj < 10:
        logging.error("test num < 10: "+projectName)
        os.remove(zipsDir + projectName + '.zip')
        return False
    return True

def countTestNum(path: str)-> int:
    test_count = 0

    # 获取当前目录下的文件列表
    file_list = os.listdir(path)
    # 遍历文件列表，如果当前文件不是文件夹，则文件数量+1，如果是文件夹，则文件夹数量+1且再调用统计文件个数的方法
    for i in file_list:
        path_now = path + os.path.sep + i
        if os.path.isdir(path_now):
            # folder_count=folder_count+1
            test_count += countTestNum(path_now)
        elif path_now.endswith('.java'):
            try:
                with open(path_now, 'r', encoding='utf-8') as test_file:
                    all_text = test_file.read()
                    test_count += all_text.count("@Test")
            except Exception as e:
                with open(path_now, 'r', encoding='ISO-8859-1') as test_file:
                    all_text = test_file.read()
                    test_count += all_text.count("@Test")

    return test_count


def unzip_single(src_file, dest_dir, password):
    ''' 解压单个文件到目标文件夹。
    '''
    if password:
        password = password.encode()
    zf = zipfile.ZipFile(src_file)
    try:
        zf.extractall(path=dest_dir, pwd=password)
    except Exception as e:
        logging.error(f"Error extracting {src_file}: {e}")
        return
    finally:
        zf.close()


def unzip_all(source_dir, dest_dir, password):
    if not os.path.isdir(source_dir):    # 如果是单一文件
        unzip_single(source_dir, dest_dir, password)
    else:
        it = os.scandir(source_dir)
        for entry in it:
            if entry.is_file() and os.path.splitext(entry.name)[1] == '.zip':
                unzip_single(entry.path, dest_dir, password)


def get_results(url):
    headers = {'User-Agent': 'Mozilla/5.0',
               'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Authorization': ' token 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'
               }
    req = Request(url, headers=headers)
    response = urlopen(req, timeout=10).read()
    result = json.loads(response.decode())
    return result


def hasGradleFile(contents):
    for content in contents:
        fileName = str(content['name'])
        if fileName == "build.gradle":
            return True
    return False


def hasPomFile(contents):
    for content in contents:
        fileName = str(content['name'])
        if fileName == "pom.xml":
            return True
    return False


def toTimestamp(recentCommitDate):
    timestamp = time.mktime(time.strptime(
        recentCommitDate, "%Y-%m-%dT%H:%M:%SZ"))
    return timestamp


def isRecentCommit(recentCommitDateTimestamp):
    # Judge if the recent commit is within 30 days
    if time.time() - recentCommitDateTimestamp < 30 * 24 * 60 * 60:
        return True
    return False



# 爬取之前，先在github上申请一个token，现在这个token是我已申请的token，你需要重新申请一个，填充到get_results方法中的Authorization字段
# 爬虫大致思路就是通过github api访问项目列表，然后筛选项目，通过urlretrieve爬下来zip，然后本地如果还需要进一步筛选可以在本地进一步筛
# 维护哪些项目已经爬了哪些没爬的信息是通过mysql数据库管理，放在指定database的指定table里。需要你提前安装mysql和建表，
# 比如在这个脚本是放在new_enterprise的指定table githubprojectstest里面。可以根据需要自行更改表名数据库名和用户名
# 但这个代码写的不太好，要改要注意都改，比如execQuerySQL和execInsertSQL函数都硬编码了数据库名和用户名
# 注意爬虫爬一次后要sleep至少两秒。因为github的最大访问限制是每分钟30次，超过这个限制会被封token和ip
# iteration time
def run():
    loggingconfig()
    print("zipsDir: " + zipsDir)
    print("unzipsDir: " + unzipsDir)
    print("temp_unzips_dir: " + temp_unzips_dir)
    print("max_crawling_single_time_num: " + str(max_crawling_single_time_num))
    # iter var
    download_num = 0
    selected_num = 0
    if not os.path.isdir(zipsDir):
        os.makedirs(zipsDir)
    if not os.path.isdir(unzipsDir):
        os.makedirs(unzipsDir)
    if not os.path.isdir(temp_unzips_dir):
        os.makedirs(temp_unzips_dir)

    # 通过github提供的api接口来爬项目（可以在浏览器访问一下这个giturl，看看长什么样）
    for ch in range(0, 26):
      for i in range(0, 50):
            giturl = 'https://api.github.com/search/repositories?q=%s&sort=stars&order=desc&language:java&page=%i&per_page=20' % ( chr(ch + ord('a')) +"+stars:>100+language:java", i)
            logging.debug(giturl)
            try:
                items = get_results(giturl)
                time.sleep(2)
                for item in items['items']:
                    time.sleep(2)
                    try:
                        projectName = str(item['name']).replace(
                            ".", "-").replace("_", "-")
                        stargazersCount = item['stargazers_count']
                        size = item['size']
                        # 筛选 star数大于100的（可自行调整下限）
                        if stargazersCount < 100:
                            logging.error(f"{projectName} stargazersCount < 100")
                            continue
                        # 筛除过大的项目，大于100MB算过大（可自行调整上限）
                        if size > 100 * 1024 * 1024:
                            logging.error(f"{projectName} size > 100 * 1024 * 1024")
                            continue
                        htmlUrl = item['html_url']
                        contentsUrl = str(item['contents_url']).replace(
                            "/{+path}", "")
                        contents = get_results(contentsUrl)
                        # 因为我是爬Maven项目，所以要筛除没有Pom文件的项目
                        isMaven = hasPomFile(contents)
                        isGradle = hasGradleFile(contents)
                        # print(isMaven)
                        # print(isGradle)
                        recenttUpdateDate = item['pushed_at']
                        recenttUpdateDateTimestamp = toTimestamp(recenttUpdateDate)
                        # 筛除近期commit的项目（可根据需要删除这个判断）
                        releaseUrl = str(
                            item['releases_url']).replace("{/id}", "")
                        releases = get_results(releaseUrl)
                        version = item['default_branch']
                        downloadUrl = htmlUrl + '/archive/' + version + '.zip'
                        if releases:
                            version = releases[0]['tag_name']
                            downloadUrl = releases[0]['html_url'].replace(
                                "releases/tag", "archive") + ".zip"
                        if not isMaven:
                            logging.error(projectName + "不是Maven项目")
                            continue
                        if not isRecentCommit(recenttUpdateDateTimestamp):
                            logging.error(projectName + "不是近期commit的项目,最近commit时间:" + recenttUpdateDate)
                            continue
                        # 这个脚本是通过Mysql来管理哪些项目已经爬过哪些项目没爬过的。有方便也有不便的地方，可根据需要调整
                        # 这里表名是githubprojectstest，可根据需要在mysql中建表
                        logging.info(downloadUrl)
                        existInLocal = csv_helper.is_downloaded(project_name=projectName, version=version)
                        download_success = False
                        if existInLocal:
                            logging.warning(projectName + "版本:" + version + "已存在")
                        else:
                            fileName = zipsDir + projectName + ".zip"
                            download_success = download_file(downloadUrl,fileName)
                            if(not download_success):
                               continue
                            logging.info(fileName + "下载完成")
                            # 以下部分是做实验环节需要删除test数目小于一定数量的项目、删除spring项目等判断条件，用不到可以直接删除。
                            '''解压，查看test数目'''
                            if os.path.isdir(temp_unzips_dir + projectName):
                                rmdir(temp_unzips_dir + projectName)
                            os.mkdir(temp_unzips_dir + projectName)
                            unzip_single(zipsDir + projectName + '.zip', temp_unzips_dir + projectName + os.path.sep, False)
                            
                            matchCriteria = filterProjects(projectName)
                            if matchCriteria:
                                logging.info(projectName + "版本:" + version + "已保存记录")
                                csv_helper.mark_downloaded(projectName, version)
                                unzip_single(zipsDir + projectName + '.zip',
                                         unzipsDir + projectName + os.path.sep, False)
                            else:
                                logging.error(projectName + "版本:" + version + "不符合实验条件")
                                continue
                            selected_num += 1
                            logging.info("总共选择数目：" + str(selected_num))  
                            if(selected_num == 120):
                                logging.info("总共选择数目：" + str(selected_num) + "，结束")
                                return    
                    except Exception as e:
                        logging.error("item handle error")
                        time.sleep(1)
                        continue
            except Exception as e:
                print(e)
                logging.error("get search error")
                time.sleep(1)
                continue
    # unzip


def execute():
    socket.setdefaulttimeout(1200)
    # 解决下载不完全问题且避免陷入死循环
    http.client.HTTPConnection._http_vsn = 10
    http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'
    ssl._create_default_https_context = ssl._create_unverified_context
    run()


if __name__ == "__main__":
    execute()
