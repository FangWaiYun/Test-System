from pathlib import Path

asset_dir = Path("/Users/wuzhehao/Library/Mobile Documents/com~apple~CloudDocs/lab/Github/Test-System/asset")
print("绝对路径是否存在：", asset_dir.exists())
print("路径是否为目录：", asset_dir.is_dir())

print("\n列出该目录下所有文件：")
for file in asset_dir.iterdir():
    print("🧾", file.name, "| is_file:", file.is_file())