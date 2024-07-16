<div align="center">
	<img src="https://7trees.cn/static/favicon.ico" width="160" />
	<h1>zyMusic</h1>
</div>




> [!NOTE]
> 如果您觉得 `zyMusic`对您有所帮助，或者您喜欢我们的项目，请在 GitHub 上给我们一个 ⭐️。您的支持是我们持续改进和增加新功能的动力！感谢您的支持！

**更新日志**
  - [查阅](https://7trees.cn/blog/zyMusic)

## 预览

- [地址](http://y.7trees.cn)

## 技术组成

- **Python Flask**
- **React**


## 功能特点
暂未更新

## 示例图片

![](https://7trees.cn/zyImg/test/357b2ce2ea9c912e94d4209ae5087370.png)

## 如何运行

后台服务:
1. 确保你的系统已经安装了 Python 和 pip。
2. 克隆或下载 zyMusic 代码库到本地。创建一个数据库，导入本项目里的 *sql* 文件，配置 *config.ini*
3. 在终端中进入项目根目录，并执行以下命令的顺序执行以启动 zyMusic 后台程序：

```bash
$ pip install -r requirements.txt
$ python wsgi.py
```

前台服务:
1. 确保你的系统已经安装了并配置了 node 环境 
2. 进入 项目根目录/web ，配置 *config.js* 以供程序连接到后台服务
3. 在终端中执行以下命令的顺序执行以启动 zyMusic 前台程序

```bash
$ npm install
$ npm start
```

4. 在浏览器中访问 `http://localhost:3000`，即可进入 zyMusic。


音乐数据导入（仅支持.mp3）:
1. ok,在此项目之前确保你的数据库已经成功创建
2. 进入 项目根目录 ，你可以使用python `autoCreate.py` 来为你的数据库导入数据
3. 在终端中执行以下命令的顺序执行以启动 zyMusic 前台程序

```bash
$ npm install
$ npm start
```

4. 在浏览器中访问 `http://localhost:3000`，即可进入 zyMusic。

## 开源贡献者

感谢以下各位的贡献

<img src="https://contrib.rocks/image?repo=Athenavi/zyMusic" />

## 交流

暂无开放


## 免责声明

zyMusic 是一个个人项目，并未经过详尽测试和完善，因此不对其能力和稳定性做出任何保证。使用 zyMusic 时请注意自己的数据安全和程序稳定性。任何由于使用 zyMusic 造成的数据丢失、损坏或其他问题，作者概不负责。

**请谨慎使用 zyMusic，并在使用之前备份你的数据。**

