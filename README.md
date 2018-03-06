# telegram-bot-moshare  
通过telegram bot在moshare（phpwind论坛）网站登录，发帖，打卡  

## 准备工作
1,安装python3  
2,创建telegram bot,获取token  
3,git clone https://github.com/zhongfly/telegram-bot-moshare.git  
4,安装依赖 pip install -r requirements.txt  
5,在postman.py中填入moshare的账号信息（根据网络情况设置代理），在bot.py中填入telegram bot的token（根据网络情况设置代理）  

## 使用说明  
运行bot.py  
在telegram bot中发送 /start 了解所有命令  

### 登录  
在postman.py中填入登录信息  
在telegram bot中发送 /login 然后按照提示进行登录  

### 检查登录状态  
在telegram bot中发送 /islogin  

### 发帖  
仅支持在acg文章转载区发送纯转新闻贴  
在telegram bot中发送 /post 后按提示发送新闻网站的文章链接给bot（目前仅支持acgdog及dmzj）  
bot会自动处理文章，并将即将发帖的标题回复给你  
确认无误后，选择确认即可发帖，bot会返回发帖结果  

### 每日打卡  
在telegram bot中发送 /dailybonus  
