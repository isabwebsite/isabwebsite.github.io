#!/bin/zsh
cd -- "${0:A:h}"
python3 tools/preview.py
if [[ $? -ne 0 ]]; then
  print '预览没有启动。把上方提示交给 AI，并让它阅读 README.md。按回车关闭。'
  read
fi
