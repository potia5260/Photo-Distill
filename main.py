import shutil
import hashlib
from pathlib import Path
from collections import defaultdict

def get_file_md5(file_path):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def delete_mov_files(folders):
    """删除所有.mov文件"""
    for folder in folders:
        for mov_file in Path(folder).rglob("*.mov"):
            mov_file.unlink()


def deduplicate_and_copy(src_folders, dest_folder):
    """
    增强版去重逻辑（增加MD5校验）：
    - 文件名 + 扩展名 + MD5 全相同 → 保留第一个
    - 文件名 + 扩展名相同但MD5不同 → 生成带序号的新文件名
    """
    file_map = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    # 构建包含MD5的三层映射字典
    for folder in src_folders:
        for ext in ("*.jpg", "*.heic"):
            for file_path in Path(folder).rglob(ext):
                file_name = file_path.stem
                file_ext = file_path.suffix.lower()
                file_md5 = get_file_md5(file_path)
                file_map[file_name][file_ext][file_md5].append(file_path)

    # 创建目标文件夹
    dest_path = Path(dest_folder)
    dest_path.mkdir(parents=True, exist_ok=True)

    # 处理文件复制（自动生成序号防冲突）
    for file_name, exts in file_map.items():
        for ext, md5_group in exts.items():
            # 对同扩展名的MD5组按哈希值排序（保证生成顺序稳定）
            sorted_md5 = sorted(md5_group.items(), key=lambda x: x[0])

            for idx, (md5_val, paths) in enumerate(sorted_md5):
                source_file = paths[0]  # 取每组第一个文件

                # 生成目标文件名
                if idx == 0:
                    target_name = f"{file_name}{ext}"  # 首文件保留原名
                else:
                    target_name = f"{file_name}_{idx}{ext}"  # 后续文件加序号

                target_file = dest_path / target_name

                # 仅在目标不存在时复制（避免覆盖）
                if not target_file.exists():
                    shutil.copy2(source_file, target_file)


if __name__ == "__main__":
    # 配置参数
    source_folders = ["C:/照片备份/20190927手机相册备份", "C:/照片备份/20240825手机相册备份"]  # 替换为您的源文件夹
    destination_folder = "C:/照片备份/202540419手机相册备份"  # 替换为目标文件夹

    # 执行操作
    delete_mov_files(source_folders)
    deduplicate_and_copy(source_folders, destination_folder)
