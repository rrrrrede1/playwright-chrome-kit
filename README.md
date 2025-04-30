# Google Chrome + Playwright 自动化环境包

这是一个集成了便携版 Google Chrome 和 Playwright 自动化环境的项目模板。

使用了 https://github.com/rrrrrede1/Google-Chrome-Portable 的自动封装方法。

## 项目结构

   ```bash
project/
├── application/
│   ├── Chrome/         # Chrome 主程序
│   ├── UserData/       # 用户数据文件夹
│   └── start.bat       # 启动脚本
├── environment.yml     # Conda 环境配置
├── browser.py          # 基本页面操作类 
├── example.py          # 示例脚本 
└── README.md
   ```
   
这个项目结构现在包含了：
- 便携版原版 Google Chrome（不是 Chromium）
- 独立的用户数据目录
- 简单的启动脚本
- Conda 环境配置（包含 Playwright）
- 详细的使用说明
- 通过 GitHub Actions 自动更新

GitHub Actions 会：
- 每周自动更新 Chrome 到最新版本
- 保持 Playwright 和其他依赖的更新
- 生成新的便携版 Chrome 包

您可以直接使用这个模板来开发基于 **Chrome** 的自动化脚本

## 使用说明

1. 启动 Chrome：
   - 双击 `application/start.bat` 即可启动便携版 Chrome
   - 所有用户数据将保存在 `UserData` 文件夹中

2. 配置开发环境：
   ```bash
   conda env create -f environment.yml
   conda activate chrome-automation
   playwright install chromium
   ```

## 注意事项
   - UserData 文件夹用于存储浏览器配置、书签等数据
   - 首次运行时会自动创建配置文件

# 许可证

本项目采用 **[GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.html)** 许可证，任何人都可以自由使用、修改和分发本项目的代码，但有以下限制：

1. 你必须将所有修改的代码以相同的 AGPL 许可证开源
2. 如果你在网络服务中运行该项目的修改版，必须向所有访问该服务的用户提供源代码

详见 [LICENSE 文件](./LICENSE)
