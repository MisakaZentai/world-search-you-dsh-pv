# 第三方素材与许可

项目代码按 MIT 发布。以下素材不由本项目代码许可重新授权。

## 角色美术

`film/assets/character/`、`film/assets/pane/`、`film/assets/r5_fh/`、`film/ui/assets/`，以及 `film/assets/film1_egg/`、`film/assets/film1_end/` 中引用画面的角色部分，沿用 PV01 的 CC BY-NC-SA 4.0 素材链：

1. 角色原作：溟月 © 上善无形。[Pixiv](https://www.pixiv.net/users/62155430)
2. 女仆版设计：ZipZipPipe。[原帖](https://www.pixiv.net/artworks/148186519)
3. 立绘：Small-tailqwq / dsh-deep-whale。
4. 表情：[dsh-whale-galgame](https://github.com/JAdpp/dsh-whale-galgame)。

保留上游说明于 `LICENSES/artwork-sources/`，许可全文见 [CC BY-NC-SA 4.0](LICENSES/CC-BY-NC-SA-4.0.txt)。历史核实出处见 [PV01 素材来源记录](docs/PV01_ASSET_SOURCES.md)；该记录描述 2026-09-30 的核查，不表示本次重新核实全部上游网页。

本片的改动包括裁切、缩放、像素化、调色、头像合成和前作画面的局部重绘。相关美术及改编部分须署名、不得商用、按相同协议分享；这不涵盖音乐、歌词或商标。包内没有 MMD 模型、动作、H3 或 Grok 舞者缓存。

## 界面

`vendor/dsh-web-frontend/` 为 DeepSeek 前端的 CSS、用于提取图标的 JavaScript bundle，以及原 LICENSE/package.json。`film/ui/dsh_components.css` 来自 PV01 的 dsh 组件样式，保留 DeepSeek MIT 许可；代码不运行后端或读取真实会话。

bundle 包含 React、JSX runtime、React DOM 和 scheduler 的 MIT 标头；完整文本见 [React MIT](LICENSES/React-MIT.txt)。DeepSeek 商标与名称归原权利人所有。

内部塔结构的部分几何参数与制作方法参考 [pdoom-video](https://github.com/mexicat/pdoom-video)，Copyright (c) 2026 Giacomo Magnanini，MIT；保留 [对应许可](LICENSES/pdoom-video-MIT.txt)。

## 音乐、歌词、字体

- Mili 的歌曲、歌词及中文译文不随包分发。请按 [Mili 官方使用指引](https://projectmili.com/copyright-guidelines)处理成片用途及所需 AI 内容标注；本仓库不授予音乐或歌词许可。
- Consolas、微软雅黑、Segoe UI 等字体从使用者系统读取，不再分发。其他操作系统的字体替换及视觉结果尚未验证。
- `film/assets/audio/chime_g.wav` 是 PV01 自制的合成提示音。
- 角色对白与界面动作是编排的故事；技术可视化包含示意值，不是模型实验结果。

这是非官方同人作品，不表示 DeepSeek、Mili 或角色作者认可本项目。
