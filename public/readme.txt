exe文件打包命令：

pyinstaller --onefile --icon=NONE --name ollama_pull ollama_pull.py

这个命令会：
--onefile: 将所有依赖打包成单个exe文件
--icon=NONE: 使用默认图标
--name ollama_pull: 设置输出的exe文件名为ollama_pull
打包完成后，你可以在dist文件夹中找到生成的ollama_pull.exe文件。

备注：如果没有安装过pyinstaller可以使用下面的命令安装
pip install pyinstaller