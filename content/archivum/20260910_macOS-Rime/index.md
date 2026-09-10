macOS 第三方输入法方案
引擎：[鼠鬚管](https://github.com/rime/squirrel)
管理：[東風破](https://github.com/rime/plum)
词库：[雾凇拼音](https://github.com/iDvel/rime-ice)
主题：[蓝色遐想](https://github.com/hunter-ji/blue-reverie-rime-theme)

安装[鼠鬚管](https://github.com/rime/squirrel)
```bash
brew install --cask squirrel-app
```

安装[東風破](https://github.com/rime/plum)
```bash
git clone --depth 1 https://github.com/rime/plum.git plum
```
```
bash rime-install plum # 更新plum
```

安装/更新[雾凇拼音](https://github.com/iDvel/rime-ice)
```
bash rime-install iDvel/rime-ice # 安装/更新全部文件
```
```
bash rime-install iDvel/rime-ice:others/recipes/all_dicts # 仅更新词库
```

安装[蓝色遐想](https://github.com/hunter-ji/blue-reverie-rime-theme)
```bash
git clone --depth 1 https://github.com/hunter-ji/blue-reverie-rime-theme.git /tmp/blue-reverie
cp /tmp/blue-reverie/squirrel.custom.yaml ~/Library/Rime/
```

部署
```bash
# 系统设置 → 键盘 → 文字输入 → 输入法 添加「鼠须管」
open "x-apple.systempreferences:com.apple.Keyboard-Settings.extension"
```
```bash
"/Library/Input Methods/Squirrel.app/Contents/MacOS/Squirrel" --reload 2>/dev/null || true # 重新部署
```
