# Scrapy settings for sina project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os


BOT_NAME = 'sina'

SPIDER_MODULES = ['sina.spiders']
NEWSPIDER_MODULE = 'sina.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'sina (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 32
# CONCURRENT_REQUESTS_PER_IP = 16
RANDOMIZE_DOWNLOAD_DELAY = True

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
    'Referer': "https://weibo.com/"
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'sina.middlewares.SinaSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'sina.middlewares.SinaDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'sina.pipelines.SinaPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))

SINA_ACCOUNT_URL = "https://account.weibo.com/set/aj/iframe/schoollist?province=11&city=&type=1&_t=0&__rnd={}"

REDIS_SETTING = {
    "HOST": "146.56.219.98",
    "PORT": "16379",
    "PASSWORD": "Qm1lrYiMe8wx2sT7",
    "MAX_CONNECTIONS": 100
}

MYSQL_SETTING = {
    "HOST": "146.56.219.98",
    "NAME": "sina",
    "USER": "lichunxu",
    "PASSWORD": "TT4RVhRjlJUwjEj*",
    "PORT": 3506,
    # 数据库连接编码
    'DB_CHARSET': 'utf8mb4',
    # mincached : 启动时开启的闲置连接数量(缺省值 0 开始时不创建连接)
    'DB_MIN_CACHED': 10,
    # maxcached : 连接池中允许的闲置的最多连接数量(缺省值 0 代表不闲置连接池大小)
    'DB_MAX_CACHED': 10,
    # maxshared : 共享连接数允许的最大数量(缺省值 0 代表所有连接都是专用的)
    # 如果达到了最大数量,被请求为共享的连接将会被共享使用
    'DB_MAX_SHARED': 20,
    # maxconnecyions : 创建连接池的最大数量(缺省值 0 代表不限制)
    'DB_MAX_CONNECYIONS': 100,
    # blocking : 设置在连接池达到最大数量时的行为(缺省值 0 或 False
    # 代表返回一个错误<toMany......> 其他代表阻塞直到连接数减少,连接被分配)
    'DB_BLOCKING': True,
    # maxusage : 单个连接的最大允许复用次数(缺省值 0 或 False 代表不限制的复用).
    # 当达到最大数时,连接会自动重新连接(关闭和重新打开)
    'DB_MAX_USAGE': 0,
    # setsession : 一个可选的SQL命令列表用于准备每个会话，
    # 如["set datestyle to german", ...]
    'DB_SET_SESSION': None
}

WEB_PROJECT_PATH = '/www/sina/'
STATIC_DIR = os.path.join(WEB_PROJECT_PATH, 'static')

COOKIES_PATH = os.path.join(STATIC_DIR, 'sina-cookies.txt')

FINISHED_LIST_KEY = 'spider_finished:{}'

LOG_LEVEL = 'INFO'
LOG_FILE = os.path.join(PROJECT_PATH, 'spider.log')
