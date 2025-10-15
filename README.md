# -今日头条爬虫系统 - 社交媒体数据采集
一个完整的Python爬虫系统，目前支持今日头条平台的数据采集

## 使用说明
- 运行main.py文件即可，后续要爬其他页面可以直接更改pn值
- 今日头条的页面序号是从0开始计数的，故第一页的pn为0
- 主爬虫代码在toutiao_spider.py文件中，类为ToutiaoSpider

## 可爬取内容
- 标题（仅限官媒，因为头条用户的文章没有标题）
- 用户id（仅限头条用户）
- 用户昵称（仅限头条用户）
- 用户头像url（仅限头条用户）
- 头条id
- 官媒外联（仅限官媒）
- ip地址（仅限头条用户）
- 发布时间
- 爬取时间
- 是否为官媒
- 预览文（content）
- 图片数量
- 图片url(以列表形式存储)
- 转发数
- 评论数
- 赞数
- content是否为长文本
- 搜索关键词

## 项目结构

{
toutiao_crawler/
├── settings.py          # 配置文件
├── toutiao_spider.py    # 抖音爬虫
├── helpers.py          # 辅助函数
├── data/                   # 数据存储目录
├── main.py                 # 单平台主程序
├── requirements.txt        # 依赖包
└── README.md              # 说明文档
}

## 安装配置
### 1.环境要求
Python 3.8+
网络连接
### 2.安装依赖
cd toutiao_crawler
pip install -r requirements.txt
(mac:pip3 install -r requirements.txt)
### 3.爬虫配置说明

核心配置项

关键词设置

keyword：”李雨珊事件”
位置：search_toutiao()方法参数
max_pages：最大爬取页数
page_num：当前页码（从0开始）
延迟策略：delay_range=(3,6)秒随机间隔
超时设置：timeout=30秒（网络请求）

反爬虫策略

重试机制：retry_times=3次失败重试
登录检测：自动识别login重定向
验证码检测：通过验证码关键词触发警告

数据处理

批量插入：batch_size=50条/批次
数据字段：包含内容、用户、时间、互动数据等18个字段
图片处理：自动提取pic_urls并计数

