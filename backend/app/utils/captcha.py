"""
验证码工具
"""
import random
import string
import io
import base64
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

# 内存存储（生产环境建议替换为 Redis）
_captcha_store = {}


def generate_captcha(width: int = 120, height: int = 44) -> tuple[str, str]:
    """
    生成图形验证码
    
    Returns:
        (captcha_key, base64_image_url)
    """
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

    # 创建图像
    img = Image.new('RGB', (width, height), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)

    # 绘制干扰线
    for _ in range(6):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line(
            [(x1, y1), (x2, y2)],
            fill=(random.randint(150, 220), random.randint(150, 220), random.randint(150, 220)),
            width=1
        )

    # 尝试加载字体
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except Exception:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 28)
        except Exception:
            try:
                # Pillow 10+ 支持带 size 参数的 load_default
                font = ImageFont.load_default(size=28)
            except Exception:
                # 旧版本 Pillow 的默认字体较小
                font = ImageFont.load_default()

    # 绘制文字
    for i, char in enumerate(code):
        x = 15 + i * 26
        y = random.randint(4, 12)
        color = (random.randint(30, 120), random.randint(30, 120), random.randint(30, 120))
        if font:
            draw.text((x, y), char, font=font, fill=color)
        else:
            draw.text((x, y), char, fill=color)

    # 绘制干扰点
    for _ in range(150):
        x, y = random.randint(0, width), random.randint(0, height)
        draw.point((x, y), fill=(random.randint(180, 255), random.randint(180, 255), random.randint(180, 255)))

    # 转为 base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    # 存储验证码
    _captcha_store[key] = {
        'code': code,
        'expires_at': datetime.utcnow() + timedelta(minutes=5)
    }

    # 清理过期验证码
    _cleanup_expired()

    return key, f'data:image/png;base64,{img_base64}'


def verify_captcha(key: str, code: str) -> bool:
    """验证验证码"""
    if not key or not code:
        return False
    if key not in _captcha_store:
        return False

    data = _captcha_store[key]
    if data['expires_at'] < datetime.utcnow():
        del _captcha_store[key]
        return False

    if data['code'].upper() != code.upper():
        return False

    del _captcha_store[key]
    return True


def _cleanup_expired():
    """清理过期验证码"""
    now = datetime.utcnow()
    expired = [k for k, v in _captcha_store.items() if v['expires_at'] < now]
    for k in expired:
        del _captcha_store[k]
