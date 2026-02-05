"""
编码转换工具函数

处理系统 GBK 编码与项目 UTF-8 编码之间的转换
"""
import logging
import re

logger = logging.getLogger(__name__)


def clean_stock_name(name: str) -> str:
    """
    清理股票名称，去除可能的乱码和非法字符

    Args:
        name: 股票名称

    Returns:
        str: 清理后的股票名称
    """
    if not name:
        return ""

    # 去除控制字符和非法字符
    name = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(name))

    # 去除首尾空格
    name = name.strip()

    return name


def validate_chinese_name(name: str) -> bool:
    """
    验证中文名称是否有效（没有乱码）

    Args:
        name: 中文名称

    Returns:
        bool: 是否有效
    """
    if not name:
        return False

    # 检查是否包含常见乱码模式
    mojibake_patterns = [
        r'[\ufffd]',  # 替换字符
        r'[ÂÃÀÅÆÇÈÉÊË]',  # 常见的乱码字符（Latin-1 补充）
        r'\\x[0-9a-fA-F]{2}',  # 十六进制转义序列
    ]

    for pattern in mojibake_patterns:
        if re.search(pattern, name):
            return False

    # 检查是否包含有效中文字符
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', name))
    return has_chinese


def fix_gbk_mojibake(text: str) -> str:
    """
    修复 GBK 到 UTF-8 的乱码（Mojibake）

    常见情况：UTF-8 字符串被错误地当作 GBK 解码

    Example:
        "è´¢å¯" (乱码) → "财经" (正确)

    Args:
        text: 可能包含乱码的字符串

    Returns:
        str: 修复后的字符串
    """
    if not text:
        return ""

    try:
        # 尝试：当作 GBK 编码为字节，然后用 UTF-8 解码
        return text.encode('gbk').decode('utf-8')
    except (UnicodeError, AttributeError):
        # 不是 GBK 乱码，返回原字符串
        return text


def ensure_utf8(text: str) -> str:
    """
    确保字符串是 UTF-8 编码

    如果字符串是其他编码，转换为 UTF-8

    Args:
        text: 输入字符串

    Returns:
        str: UTF-8 编码的字符串
    """
    if not text:
        return ""

    # 如果已经是字符串，检查是否包含乱码字符
    try:
        # 尝试编码为 UTF-8 再解码，检测编码问题
        text.encode('utf-8').decode('utf-8')
        return text
    except UnicodeError:
        # 可能有编码问题，尝试修复
        try:
            # 尝试从 GBK 转换
            return text.encode('gbk').decode('utf-8')
        except (UnicodeError, AttributeError):
            # 无法修复，返回原字符串
            logger.warning(f"无法修复字符串编码，可能存在乱码: {text[:50]}...")
            return text
