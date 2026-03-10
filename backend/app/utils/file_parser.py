"""文件解析工具：支持多种文件格式的文本提取"""
import os
from typing import Optional, Tuple
import pypdf
from docx import Document
import aiofiles


class FileParser:
    """文件解析器类"""

    @staticmethod
    def extract_text(file_path: str, filename: str) -> str:
        """
        从文件中提取文本

        Args:
            file_path: 文件路径
            filename: 文件名

        Returns:
            提取的文本内容

        Raises:
            ValueError: 不支持的文件格式
        """
        ext = os.path.splitext(filename.lower())[1]

        if ext == '.txt' or ext == '.md':
            return FileParser._extract_text_file(file_path)
        elif ext == '.pdf':
            return FileParser._extract_pdf(file_path)
        elif ext == '.docx':
            return FileParser._extract_docx(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

    @staticmethod
    def _extract_text_file(file_path: str) -> str:
        """从文本文件中提取文本"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def _extract_pdf(file_path: str) -> str:
        """从PDF文件中提取文本"""
        text = []
        with pypdf.PdfReader(file_path) as reader:
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text.append(extracted)
        return '\n'.join(text)

    @staticmethod
    def _extract_docx(file_path: str) -> str:
        """从DOCX文件中提取文本"""
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小（字节）"""
        return os.path.getsize(file_path)

    @staticmethod
    def is_supported(filename: str) -> bool:
        """检查文件格式是否支持"""
        ext = os.path.splitext(filename.lower())[1]
        return ext in ['.txt', '.md', '.pdf', '.docx']

    @staticmethod
    async def save_uploaded_file(file_content: bytes, filename: str, upload_dir: str) -> str:
        """
        保存上传的文件

        Args:
            file_content: 文件内容
            filename: 文件名
            upload_dir: 上传目录

        Returns:
            保存后的文件路径
        """
        # 创建子目录按照文件名哈希
        import hashlib
        file_hash = hashlib.md5(filename.encode()).hexdigest()
        subdir = file_hash[:2]

        target_dir = os.path.join(upload_dir, subdir)
        os.makedirs(target_dir, exist_ok=True)

        # 生成唯一文件名
        timestamp = str(int(time.time() * 1000))
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(target_dir, unique_filename)

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)

        return file_path


import time
