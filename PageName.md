# 介绍 #

贼惦记，采用Python写的开心网外挂程序。目前的主要功能是偷菜。
  * 自动检查自家菜园子,把成熟的菜收了
  * 自动检查"已成熟"的朋友家,把能收的菜收了
  * 自动判断哪些菜地"已偷过","已偷光",不该出手时绝不出手.
  * 免偷名单功能,避免偷了不想偷的菜.(由于开心网对每日偷菜的次数是有限制的,偷太多便宜的菜像牧草之类就很不合算了)


# 安装 #

程序依赖于Python2.6,由于更新频繁,无暇制作各平台下的安装包,建议用户安装Python2.6.
安装步骤如下:

  1. 安装Python2.6 (_已安装的同学可以跳过这步_)
    * Windows 用户可直接点击[Windows x86 MSI Installer (2.6)](http://www.python.org/ftp/python/2.6/python-2.6.msi)
    * 其它用户可以在Python2.6官方页面找到安装程序:http://www.python.org/download/releases/2.6/
  1. 下载zeidianji.py,http://zeidianji.googlecode.com/files/zeidianji.py 直接双击运行.
  1. 如果您需要进一步的定制功能,例如免偷列表功能.请下载config.ini,和zeidianji.py放在同一目录中.打开config.ini,在"account\_name="后填上您的开心网用户名,在"account\_password="后填上您的开心网密码.