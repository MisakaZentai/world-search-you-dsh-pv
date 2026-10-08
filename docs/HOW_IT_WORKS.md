# 构建与修改

每一帧是歌曲时间 t 的函数。`film/tl.py` 读取逐词时间和逐拍时间；`film/groups/` 绘制终端，`film/inside/` 绘制内部结构示意，`film/ui/pages/` 返回同一时刻的 HTML。

`data/r21.json` 固定上传版的开关。构建入口清除继承的 `DSH_*` 变量，防止当前 shell 的试验开关混入。文件名含旧版本号的模块是 r21 的函数依赖，不能按名字直接删除。

`data/page_recipes.json` 记录生产截图的帧号、时间、窗口大小和页面函数。默认从 `data/pages/*.json.xz` 读取上传版的逐帧 HTML 快照（含当时的局部更新），截图工具将 CSS 动画锁定到歌曲时间。`--from-source` 改为从页面函数生成 HTML，供修改时使用；部分页面源码与上传版截图不同，两种模式的区别见 README。图片、CSS、JS 源和字体都从本地读取。

内部图版优先读本地生成缓存，缺失时现场绘制。公开包只保留音量包络这一分析缓存；页面截图与图版缓存不随包分发。

`build.py render` 输出无损母版，然后从自备 WAV 补齐尾部静音、混提示音、转 BT.709 并编码。音频统一重采样为 44.1 kHz。4K 是 720p 的三倍最近邻放大。`encode --output-dir out_export` 复用已有母版，转码到一个新的目录；母版始终位于 `out/`。为保留失败诊断，分段母版保留在 `out/_segments_*`，程序不会自动删除；修改画面后重渲染请使用新工作副本。

不同 Python/Pillow/Chromium/字体版本可能影响抗锯齿或排版。Windows 是本次验证目标；macOS/Linux 的路径本身可解析，但字体和完整构建未验收。
