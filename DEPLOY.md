# 🚀 Render 部署傻瓜式指南

> 前提：你已经下载了 prompt-tool 文件夹里的全部代码。
> 预计时间：20 分钟（一次性操作，以后改代码自动更新）

---

## 第一步：注册 GitHub 账号（如已有请跳过）

1. 打开 https://github.com
2. 点击右上角「Sign up」注册
3. 验证邮箱

---

## 第二步：安装 GitHub Desktop（不用命令行）

1. 打开 https://desktop.github.com/
2. 下载安装
3. 登录你的 GitHub 账号

---

## 第三步：创建 GitHub 仓库并上传代码

1. 打开 GitHub Desktop
2. 点击菜单：「File」→「New Repository」
3. 填写：
   - Name：`prompt-tool`
   - Local Path：选择你电脑上 `prompt-tool` 文件夹的【上一级目录】
   - ☑️ 勾选「Initialize with a README」
4. 点击「Create Repository」
5. 它会自动识别文件夹中的所有文件
6. 左下角的 Summary 框写：`initial commit`
7. 点击「Commit to main」
8. 点击右上角「Publish repository」
9. 弹窗中取消勾选「Keep this code private」（Render 免费版需要公开仓库）
10. 点击「Publish Repository」

✅ 代码已上传到 GitHub。

---

## 第四步：注册 Render

1. 打开 https://render.com
2. 点击「Get Started for Free」
3. 选择「Sign in with GitHub」（用 GitHub 账号登录，最方便）
4. 授权 Render 访问你的 GitHub

---

## 第五步：创建 Web Service

1. 登录 Render 后，点击右上角「New +」→「Web Service」
2. 选择「Build and deploy from a Git repository」→ Next
3. 找到你的 `prompt-tool` 仓库，点击「Connect」
4. 填写配置：

```
Name:           prompt-tool（或任何你喜欢的名字）
Region:         Singapore (Southeast Asia)（离中国最近）
Branch:         main
Runtime:        Python 3
Build Command:  pip install -r requirements.txt
Start Command:  uvicorn app.main:app --host 0.0.0.0 --port $PORT
Instance Type:  Free ← 选这个！
```

5. 先不要点 Deploy！往下滚动到「Environment Variables」

---

## 第六步：设置环境变量（API Key）

在「Environment Variables」区域，点击「Add Environment Variable」：

**必填（至少一个供应商）：**

| Key | Value |
|-----|-------|
| `DEEPSEEK_API_KEY` | 你的 DeepSeek API Key |
| `DEFAULT_PROVIDER` | `deepseek` |

**可选（想支持更多供应商就加）：**

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | 你的 OpenAI Key |
| `MOONSHOT_API_KEY` | 你的 Kimi Key |
| `ANTHROPIC_API_KEY` | 你的 Claude Key |

⚠️ 只有设置了 Key 的供应商才会在网站上显示为可用。

---

## 第七步：点击 Deploy！

1. 点击页面底部的「Create Web Service」
2. Render 开始自动构建，你会看到日志滚动
3. 等待 2-3 分钟，看到 `Your service is live 🎉` 就成功了
4. 页面顶部会显示你的网站地址，类似：
   ```
   https://prompt-tool-xxxx.onrender.com
   ```
5. 点击这个链接 → 你的网站就上线了！🎉

---

## 第八步：验证网站可用

1. 打开网站链接
2. 你应该看到：
   - 全局设定区域（风格/比例/色调/光影）
   - 角色卡输入框
   - 文件上传区域
   - AI 供应商选择栏（已配置 Key 的会亮起）
3. 上传你的 test_script.xlsx 测试一下
4. 点击「开始生成 Prompt」
5. 看到进度条滚动，最后出现下载按钮

---

## 后续：如何更新代码

以后想改代码（比如调整 Prompt、改前端样式），流程非常简单：

1. 在你电脑上修改 `prompt-tool` 文件夹中的文件
2. 打开 GitHub Desktop
3. 左侧会显示你改了哪些文件
4. 左下角写个简单描述，如 `update prompt`
5. 点击「Commit to main」
6. 点击右上角「Push origin」
7. Render 会自动检测到变更，在 1-2 分钟内自动重新部署

你不需要再登录 Render，全自动的。

---

## ⚠️ 注意事项

### Render 免费版限制

- **15 分钟无访问会休眠**：首次打开可能需要等 30-60 秒唤醒
- **每月 750 小时免费**：个人使用完全够
- **没有自定义域名**：网址是 `xxx.onrender.com` 格式

### 如果想去掉休眠

升级到 Render 付费版（$7/月），服务永不休眠。

### 如果想绑定自己的域名

1. Render Dashboard → 你的服务 → Settings → Custom Domains
2. 添加你的域名
3. 在域名服务商处添加 CNAME 记录指向 Render 给的地址

---

## ❓ 常见问题

### 构建失败，日志显示红色错误

→ 截图发给我看，大概率是 requirements.txt 某个包版本问题

### 网站打开是空白页

→ 检查 Start Command 是不是写对了：`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 上传 Excel 后报错「缺少 API Key」

→ 去 Render Dashboard → 你的服务 → Environment → 检查 Key 是否正确设置

### 生成很慢

→ 正常，免费版服务器在新加坡，调用中国的 DeepSeek API 有延迟。每批大约 5-10 秒。

### 想换供应商

→ 在 Render Dashboard → Environment 中添加对应的 Key，保存后服务自动重启，网站上就能切换了

---

## 📁 项目文件清单

```
prompt-tool/
├── app/
│   ├── __init__.py           # 空文件
│   ├── main.py               # FastAPI 入口
│   ├── config.py             # 配置
│   ├── routers/
│   │   ├── __init__.py       # 空文件
│   │   └── generate.py       # API 路由
│   ├── services/
│   │   ├── __init__.py       # 空文件
│   │   ├── excel_parser.py   # Excel 解析
│   │   ├── excel_writer.py   # Excel 输出
│   │   └── llm_client.py     # LLM 多供应商调用
│   ├── prompts/
│   │   ├── __init__.py       # 空文件
│   │   ├── premium.py        # 优质模型 Prompt
│   │   └── opensource.py     # 开源模型 Prompt
│   └── static/
│       └── index.html        # 前端页面
├── requirements.txt          # Python 依赖
├── Dockerfile                # Docker 部署（备用）
├── render.yaml               # Render 配置
├── .env.example              # 环境变量模板
├── .gitignore                # Git 忽略规则
└── README.md                 # 项目说明
```
