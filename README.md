# world.search(you); · 大肥鱼 TUI PV

Mili《world.search(you);》的非官方同人音乐影像，PV01 的续作。左边是寻找她的终端，右边是穿着她的人设说话的聊天窗口。

这是 **r21 上传版**的出片代码快照。Python/Pillow 绘制终端，Playwright 截取静态 HTML 窗口，FFmpeg 合成视频和提示音。渲染不调用语言模型，不需要模型权重或 GPU。

前作与仓库组织参考：[PV01](https://github.com/MisakaZentai/world-execute-me-dsh-pv)。

## 快速开始

已测试环境为 Windows、Python 3.12、Node 及 FFmpeg；具体检查范围见 [验证说明](docs/VERIFICATION.md)。

```text
pip install -r requirements.txt
npm install
npx playwright install chromium
```

按 [输入说明](input/README.md) 准备 `input/song.wav` 和歌词后：

```text
python build.py check
python build.py all --fetch
```

`all` 会依次检查、合成歌词时间表、重建网页截图、渲染 720p。需要同时生成 4K 时使用 `python build.py all --fetch --4k`。已有母版可以用 `python build.py encode --4k --output-dir out_export` 重新编码；所有输出均拒绝覆盖。修改绘图代码后重渲染请使用新的工作副本。

- `out/film_master.mp4`：1280×720、24 fps 无损无声母版。
- `out/film.mp4`：带原曲与提示音的 H.264 720p 版。
- `--4k`：另出三倍最近邻放大的 HEVC 版本，保留 BT.709 色彩标签。
- 片长约 304.8 秒、7315 帧；原曲结束后补静音，提示音位于 290.8 秒。
- 可单独运行 `lyrics`、`pages`、`render`、`encode`；`render --start 48 --end 50` 可出短片。先运行完整 `pages`。复用短片母版时，`encode` 使用同一组 `--start`、`--end` 参数。
- 并行度由 `--workers` 和 `--page-workers` 控制。CPU 渲染；不会启动模型服务。

## 开源包与原片的边界

歌曲、歌词全文、中文歌词翻译、歌词 tokenizer IDs、Windows 字体、成片、研究资料和生产缓存不随仓库分发。

默认从使用者自备的 LRC（或显式 `--fetch` 从 LRCLIB 获取）重建英文字幕。**未提供可使用的中文字幕及 token IDs 时，中文字幕和相应编号省略**，因此默认重建与 r21 原片有字幕差异。可选输入及其校验格式见 [input/README.md](input/README.md)。角色对白是本片叙事代码的一部分，不是私人会话记录。

保留了少量 PV01 画面引用、立绘和派生头像，其许可与代码分开。r22 试片、实际模型测量实验及生成环境不在这个版本里。画面上的模型结构、概率、logit lens 等是 r21 的叙事示意，不能作为真实推理测量数据。

**页面快照**：上传版使用的部分网页截图早于现存页面源码。默认使用 `data/pages/*.json.xz` 内的逐帧 HTML 快照重新截图，保留上传版的滚动位置和标签；它们不是图片或私人聊天记录。修改页面时可用 `build.py pages --from-source`，但这一模式会产生已记录的源码/旧截图差异，不能称为原样重建 r21。

## 目录

| 路径 | 用途 |
|---|---|
| `build.py` | 固定 r21 配置和 CPU 构建流程 |
| `film/` | 时间线、A–H 各组、字幕、终端和聊天页面 |
| `runtime/tuikit/` | 本仓库自带的 TUI 渲染器及截图工具 |
| `data/` | 不含歌词文字的时间、排版关系、截图范围、音源指纹 |
| `tools/` | 歌词重建和网页截图编排 |
| `vendor/` | dsh 前端 CSS 与图标来源 bundle，保留原许可 |
| `input/` | 使用者本地输入，Git 忽略 |
| `docs/` | 构建原理、验证和素材来源 |

## 许可与署名

项目代码：MIT，见 [LICENSE](LICENSE)。美术及其改编部分：CC BY-NC-SA 4.0。音乐、歌词、商标和字体有各自的权利边界，见 [NOTICE.md](NOTICE.md)。代码许可不授予音乐或歌词的再分发权。

音乐：Mili - world.search(you);。角色：溟月 © 上善无形 / 女仆版 ZipZipPipe / 立绘 dsh-deep-whale（Small-tailqwq）/ 表情 dsh-whale-galgame。界面致敬 DeepSeek Harness。非官方同人作品，与相关作者及官方无从属或合作关系。
