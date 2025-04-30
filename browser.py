import logging
from typing import Optional, Dict, Any
from pathlib import Path
from contextlib import suppress
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Browser as PlaywrightBrowser
from playwright.sync_api import BrowserContext, Page, Playwright

logger = logging.getLogger(__name__)

@dataclass
class BrowserConfig:
    """浏览器配置数据类"""
    # 基本设置
    viewport: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    
    # 系统和浏览器特征
    locale: str = "zh-CN"
    timezone_id: str = "Asia/Shanghai"
    
    # 硬件特征
    is_mobile: bool = False
    has_touch: bool = False
    
    # 浏览器特征注入脚本
    init_script: str = """
    Object.defineProperty(navigator, 'vendor', { get: () => 'Google Inc.' });
    Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
    Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 16 });
    
    // WebGL 参数
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) {
            return 'Google Inc. (NVIDIA)';
        }
        if (parameter === 37446) {
            return 'ANGLE (NVIDIA, NVIDIA GeForce RTX 4060 Ti (0x00002803) Direct3D11 vs_5_0 ps_5_0, D3D11)';
        }
        return getParameter.apply(this, arguments);
    };
    """
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于传递给 Playwright"""
        return {
            "viewport": self.viewport,
            "user_agent": self.user_agent,
            "locale": self.locale,
            "timezone_id": self.timezone_id,
            "is_mobile": self.is_mobile,
            "has_touch": self.has_touch
        }

class BrowserException(Exception):
    """浏览器操作相关的自定义异常类"""
    pass

class Browser:
    """同步浏览器管理类，用于控制 Playwright 浏览器实例"""
    
    def __init__(self, headless: bool = False, config: Optional[BrowserConfig] = None):
        """
        初始化浏览器管理器
        
        Args:
            headless: 是否以无头模式运行浏览器
            config: 浏览器配置，如果为None则使用默认配置
        """
        self.playwright: Optional[Playwright] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.headless = headless
        self.config = config or BrowserConfig()
        
        # 初始化路径配置
        self.base_path = Path(__file__).parent.parent.parent
        self.app_path = self.base_path / 'Application'
        self.chrome_path = self.app_path / 'chrome.exe'
        self.user_data_dir = self.app_path / 'UserData'

    def _init_environment(self) -> None:
        """
        初始化运行环境，确保必要的目录和文件存在
        
        Raises:
            BrowserException: 当环境初始化失败时抛出
        """
        try:
            self.user_data_dir.mkdir(parents=True, exist_ok=True)
            
            if not self.chrome_path.exists():
                raise FileNotFoundError(f"Chrome 可执行文件未找到: {self.chrome_path}")
                
        except Exception as e:
            logger.error(f"环境初始化失败: {e}")
            raise BrowserException(f"初始化环境失败: {str(e)}")

    def start(self) -> None:
        """
        启动浏览器并初始化页面
        
        Raises:
            BrowserException: 当浏览器启动失败时抛出
        """
        if self.playwright is not None:
            logger.info("浏览器已经启动")
            return
            
        try:
            self.playwright = sync_playwright().start()
            
            browser_args = {
                'user_data_dir': str(self.user_data_dir),
                'executable_path': str(self.chrome_path),
                'headless': self.headless,
                'args': ['--start-maximized'],
                **self.config.to_dict()
            }
            
            self.context = self.playwright.chromium.launch_persistent_context(**browser_args)
            self.page = self.context.new_page()
            
            # 初始化页面配置
            self._configure_page()
            
        except Exception as e:
            logger.error(f"浏览器启动失败: {e}")
            self.close()
            raise BrowserException(f"启动浏览器失败: {str(e)}")

    def _configure_page(self) -> None:
        """配置页面初始化脚本和等待页面加载完成"""
        self.page.add_init_script(self.config.init_script)
        self.page.wait_for_load_state('networkidle')

    def navigate_to(self, url: str, timeout: int = 30000) -> None:
        """
        导航到指定页面
        
        Args:
            url: 目标URL
            timeout: 导航超时时间（毫秒）
            
        Raises:
            BrowserException: 当页面导航失败时抛出
        """
        if not url:
            raise ValueError("URL不能为空")
            
        try:
            url = url.rstrip('/')
            # 首先等待页面导航完成
            self.page.goto(url, wait_until='domcontentloaded', timeout=timeout)
            
            try:
                # 尝试等待网络空闲，但不影响主流程
                self.page.wait_for_load_state('networkidle', timeout=5000)
            except Exception as e:
                logger.debug(f"等待网络空闲超时，继续执行: {e}")
            
        except Exception as e:
            logger.error(f"页面导航失败: {e}")
            raise BrowserException(f"页面导航失败: {str(e)}")

    def close(self) -> None:
        """安全关闭浏览器及清理资源"""
        try:
            with suppress(Exception):
                if self.context:
                    # 关闭所有页面
                    for page in self.context.pages:
                        page.close()
                    self.context.close()
                
                # 停止 playwright 实例
                if self.playwright:
                    self.playwright.stop()
                    
        except Exception as e:
            logger.error(f"关闭浏览器时出错: {e}")
        finally:
            # 清理所有实例引用
            self.page = self.context = self.playwright = None

    def __enter__(self) -> 'Browser':
        """同步上下文管理器入口"""
        self._init_environment()
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """同步上下文管理器出口"""
        self.close()

# # 使用上下文管理器方式（推荐）
# def main():
#     # headless=False 表示以有界面方式启动浏览器
#     with Browser(headless=False) as browser:
#         # 访问指定网页
#         browser.navigate_to("https://www.taobao.com")
#         # 进行其他操作...

# # 或者手动管理方式
# def manual_usage():
#     browser = Browser(headless=True)  # 无界面模式
#     try:
#         browser._init_environment()  # 初始化环境
#         browser.start()  # 启动浏览器
#         browser.navigate_to("https://www.taobao.com")
#         # 进行其他操作...
#     finally:
#         browser.close()  # 关闭浏览器

# 自定义配置
# custom_config = BrowserConfig(
#     viewport={"width": 1366, "height": 768},
#     user_agent="自定义UA字符串"
# )
# browser = Browser(headless=False, config=custom_config)