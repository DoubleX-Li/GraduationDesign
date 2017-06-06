# 部署说明

## 环境准备

### 安装Python 3.6

点击`GraduationDesign\extra_resource`中的`python-3.6.1-amd64.exe`，安装Python 3.6.1。

### 安装virtualenv

点击win+R，输入powershell打开powershell。在powershell中，输入

```bash
pip install virtualenv
```

### 更改powershell脚本执行权限

同上，在powershell中输入

```bash
Set-ExecutionPolicy unrestricted
```

使得powershell可以执行未签名的`.ps1`脚本

## 数据抓取部分

进入`GraduationDesign\jd`目录，执行命令

```bash
virtualenv --no-site-packages venv
```

待命令执行完成后，再执行命令

```bash
.\venv\Scripts\activate.ps1
```

激活virtualenv虚拟环境

接着执行命令

```bash
pip install -r .\requirements.txt
```

安装requirements.txt中列出的python的第三方库

然后执行命令

```bash
pip install ..\extra_resource\pywin32-221-cp36-cp36m-win_amd64.whl
```

安装无法直接通过pip安装的第三方库

最后，执行命令

```bash
python .\run.py
```

启动爬虫项目，抓取到的评论信息会保存在`GraduationDesign\jd`目录下的`test.db`文件中

通过修改`run.py`中的3行`id=`

```python
from scrapy import cmdline

id = '4510588'
cmd = 'scrapy crawl jd -a product_id={0} -a url=https://item.jd.com/{0}.html'.format(id)
cmdline.execute(cmd.split())
```

为要抓取的京东商城商品id，可以抓取不同的京东商城商品的评论信息。

PS：记得退出此项目后要在powershell中执行

```bash
deactivate
```

关闭虚拟环境。

## 数据分析及展示部分

进入`GraduationDesign\comment_analysis`目录，执行命令

```bash
virtualenv --no-site-packages venv
```

待命令执行完成后，再执行

```bash
.\venv\Scripts\activate.ps1
```

激活virtualenv虚拟环境

执行命令

```bash
pip install -r .\requirements.txt
```

安装此项目所需的python第三方库

接着执行命令

```bash
python .\comment_analysis
.py runserver
```

启动项目

在浏览器中访问地址`http://127.0.0.1:5000/general`，可以看到项目成功运行。