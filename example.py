from browser import Browser, BrowserConfig

def main():
    # 创建自定义浏览器配置（可选）
    custom_config = BrowserConfig(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    # 使用上下文管理器方式启动浏览器（推荐）
    with Browser(headless=False, config=custom_config) as browser:
        # 访问网页
        browser.navigate_to("https://www.baidu.com")
        
        # 等待搜索框出现并输入内容
        search_input = browser.page.get_by_id("kw")
        search_input.fill("Python自动化")
        
        # 点击搜索按钮
        search_button = browser.page.get_by_id("su")
        search_button.click()
        
        # 等待搜索结果加载
        browser.page.wait_for_load_state("networkidle")
        
        # 获取搜索结果
        results = browser.page.query_selector_all(".result.c-container")
        
        # 打印搜索结果标题
        for result in results[:5]:  # 只打印前5个结果
            title = result.query_selector("h3")
            if title:
                print(title.inner_text())

if __name__ == "__main__":
    main()