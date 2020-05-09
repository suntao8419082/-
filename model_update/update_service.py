#!/usr/bin/env python
# encoding: utf-8
'''
@author: suntao
@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
@contact: tao.sun@allsenseww.com
@software: garner
@file: update_service.py
@time: 2020/4/15 10:43
@desc:
'''

import jenkins
import os
import urllib
import zipfile
from subprocess import Popen, PIPE
from configobj import ConfigObj

config_ini = r"./config.ini"
config = ConfigObj(config_ini, encoding='utf-8')

class UpdateService():

    def __init__(self):
        self.base_url = config["jenkins"]["base_url"]
        self.api_token = config["jenkins"]["api_token"]
        self.name = config["jenkins"]["user_name"]
        self.job_name = config["service"]["job_name"]
        self.namespace = config["service"]["namespace"]
        self.pod_name = config["service"]["pod_name"]
        self.test_dir = config["service"]["test_dir"]

    def get_job_info(self):
        """获取最近一次的任务编号以及master版本的url"""
        server = jenkins.Jenkins(self.base_url, username=self.name, password=self.api_token)
        result = server.get_job_info(self.job_name, depth=1)
        for job in result["jobs"]:
            if job["name"] == "master":
                master_url = job["url"]
                last_number = job["builds"][0]["number"]
        return master_url, last_number

    def get_download_url(self, master_url, number, pck_name):
        """
        获取下载url
        :param master_url: master版本的url
        :param number: master版本的版本号
        :param pck_name:包名
        """
        download_url = master_url + str(number) + "/artifact/dist/" + pck_name
        print("download_url:" + download_url)
        return download_url

    def get_pck_name(self,number):
        pck_name = self.job_name + "-master-3.0." + str(number) + ".zip"
        return pck_name

    def download_file(self, url, number):
        mkdirlambda = lambda x: os.makedirs(x) if not os.path.exists(x) else True  # 目录是否存在,不存在则创建
        mkdirlambda(self.test_dir)
        os.chdir(self.test_dir)
        current_path = os.getcwd() + "\common-module-master-3.0." + str(number) + ".zip"
        try:
            urllib.request.urlretrieve(url, current_path)
        except Exception:
            print("文件下载失败！")

    def DecompressPck(self,pck_name):
        """解压文件"""
        file = zipfile.ZipFile(pck_name, mode='r')
        file_list = file.namelist()
        for f in file_list:
            file.extract(f)
        file.close()

    def get_pod_id(self):
        """获取pod_id"""
        commond = "kubectl get pods --namespace " + self.namespace
        p = Popen(commond, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        output = p.stdout.read()
        for i in str(output).split():
            if self.pod_name in i:
                pod_id = i.split("\\n")[1]
                print("podId:{0}".format(pod_id))
                return pod_id

    def splice_command(self,service_name, pod_id):
        """拼接和执行换包命令"""
        command = "kubectl cp  {0}  test/{1}:/usr/share/nginx/html".format(service_name, pod_id)
        print(command)
        os.system(command)
        return command

    def update_latest_version(self, service_name):
        """更新至最新版本"""
        master_url, last_number = UpdateService.get_job_info(self)
        pck_name = UpdateService.get_pck_name(self, last_number)
        download_url = UpdateService.get_download_url(self, master_url, last_number, pck_name)
        UpdateService.download_file(self, download_url, last_number)
        UpdateService.DecompressPck(self, pck_name)
        pod_id = UpdateService.get_pod_id(self)
        UpdateService.splice_command(self, service_name, pod_id)

    def update_appoint_version(self,service_name, num_verion):
        """更新至指定版本"""
        master_url, last_number = UpdateService.get_job_info(self)
        pck_name = UpdateService.get_pck_name(self,num_verion)
        download_url = UpdateService.get_download_url(self, master_url, num_verion, pck_name)
        UpdateService.download_file(self,download_url, num_verion)
        UpdateService.DecompressPck(self,pck_name)
        pod_id = UpdateService.get_pod_id(self)
        UpdateService.splice_command(self, service_name, pod_id)

if __name__ == "__main__":
    op = UpdateService()
    # op.update_latest_version("service-web-workorder-management2")
    op.update_appoint_version("service-web-production-monitoring","626")