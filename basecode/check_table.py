# -*- coding: utf-8 -*-

import re
import os
import json
import calendar
import requests
from requests.auth import HTTPBasicAuth
from flask import Flask
from flask import request
from pyrfc3339  import parse
from datetime import datetime, timedelta
from basecode.table_config import *
from basecode.CheckTable import lib

def run_cmd(*args):
    cmd = ' '.join(args)
    return os.popen(cmd).read()

def utc_to_local(rfc_str):
    utc_dt = parse(rfc_str)
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    assert utc_dt.resolution >= timedelta(microseconds=1)
    dt = local_dt.replace(microsecond=utc_dt.microsecond)
    return str(dt)


def dump_commit(commit, branch, repository):
    md5 = commit["id"]
    message = commit["message"]
    committer = commit["author"]["name"]
    timestamp = utc_to_local(commit["timestamp"])
    url = commit["url"]
    s = '>committer: %s\n>message: %s\n>time: %s\n>repository: %s\n>branch: %s\n>md5: %s\n>url: %s\n' % \
    (committer, message, timestamp, repository, branch, md5, url)
    return s



def dump_info(payload):
    branch = payload["ref"]
    repository = payload["repository"]["full_name"]
    ret = []
    for commit in payload["commits"]:
        m = re.findall('\#([0-9]+)', commit["message"])
        if m is not None:
            for issues in m:
                s = dump_commit(commit, branch, repository)
                post_url = "https://account-self.ejoy.com:8444/issues/%s.json" % (issues)
                ret.append({"post": post_url, "msg": s})
    return ret


def post_redmine_issues(payload):
    username = robot_account["username"]
    password = robot_account["password"]
    ret = dump_info(payload)
    for entry in ret:
        data = {
                "issue": {
                    "notes": entry["msg"],
                    }
                }
        resp = requests.put(entry["post"], json=data, auth=HTTPBasicAuth(username, password), timeout=10)

def parse_commits(payload):

    switch_branch(payload["ref"])

    change_files=[]

    for commit in payload["commits"]:

        change_files.extend(commit["added"])

        change_files.extend(commit["modified"])        

    cases=get_changed_cases(change_files)

    checked= run_cases(cases)
    # 将检查结果发送钉钉消息
    if checked:
        opt.send_dingtalk()




def switch_branch(branch_name):

    branch_name = os.path.basename(branch_name)

    current_branch = str(repo.active_branch)

    if branch_name!=current_branch:
        repo.git.checkout(branch_name)

    repo.git.pull()


def run_cases(cases):

    pass 



def get_changed_cases(changed_files):
    # 获得更新的配置表列表
    cases = list()

    if not changed_files:
        lib.log(u"本次提交没有配置表修改，无需检查。", "INFO")
        return False

    # 测试用例所在的目录
    case_path = os.path.split(os.path.abspath(__file__))[0]

    for file_name in changed_files:
        cs_file = lib.find_files(file_name, case_path, ".py")

        # 找得到用例脚本就将文件添加到待执行的列表里，找不到就将表添加到无用例列表里
        if cs_file:
            cases.append(cs_file)
        else:
            lib.log(u"{}表没有对应的测试用例，建议添加。".format(file_name), "WARN")

    return cases






