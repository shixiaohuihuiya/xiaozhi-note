"""
文件上传路由
"""
import os
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from database import get_db
from models import Upload, User
from schemas.common import ResponseModel, PaginatedResponse, PaginationParams
from dependencies import get_current_active_user, get_optional_user
from config import settings

router = APIRouter()


def ensure_upload_dir():
    """确保上传目录存在"""
    today = datetime.now().strftime("%Y%m%d")
    upload_dir = os.path.join(settings.UPLOAD_DIR, today)
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir, today


@router.post("/image", response_model=ResponseModel[dict])
async def upload_image(
    file: UploadFile = File(...),
    usage_type: int = Query(1, description="用途: 1-文章封面, 2-文章内容, 3-头像"),
    article_id: Optional[int] = Query(None, description="关联文章ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """上传图片"""
    # 验证文件类型
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {file.content_type}"
        )
    
    # 读取文件内容
    content = await file.read()
    
    # 验证文件大小
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # 生成文件名
    file_ext = os.path.splitext(file.filename)[1].lower()
    if not file_ext:
        file_ext = ".png"
    unique_name = f"{uuid.uuid4().hex}{file_ext}"
    
    # 确保上传目录存在
    upload_dir, date_dir = ensure_upload_dir()
    file_path = os.path.join(upload_dir, unique_name)
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 构建访问URL
    file_url = f"/uploads/{date_dir}/{unique_name}"
    
    # 记录到数据库
    upload_record = Upload(
        user_id=current_user.id,
        original_name=file.filename,
        file_name=unique_name,
        file_path=file_path,
        file_url=file_url,
        file_type=file.content_type,
        file_size=len(content),
        file_ext=file_ext,
        usage_type=usage_type,
        article_id=article_id
    )
    db.add(upload_record)
    await db.commit()
    await db.refresh(upload_record)
    
    return ResponseModel(
        code=200,
        message="上传成功",
        data={
            "id": upload_record.id,
            "url": file_url,
            "original_name": upload_record.original_name,
            "file_size": upload_record.size_in_kb
        }
    )


@router.get("/images", response_model=ResponseModel[PaginatedResponse[dict]])
async def get_uploaded_images(
    usage_type: Optional[int] = Query(None, description="用途筛选"),
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取上传的图片列表（管理员可查看全部）"""
    query = select(Upload).options(selectinload(Upload.user))

    # 非管理员只能看自己的
    if not current_user.is_admin:
        query = query.where(Upload.user_id == current_user.id)

    if usage_type is not None:
        query = query.where(Upload.usage_type == usage_type)

    # 获取总数
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0

    # 分页查询
    query = query.order_by(desc(Upload.created_at)).offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query)
    uploads = result.scalars().all()

    data = [
        {
            "id": u.id,
            "url": u.file_url,
            "original_name": u.original_name,
            "file_type": u.file_type,
            "file_size": u.size_in_kb,
            "usage_type": u.usage_type,
            "uploader": {
                "id": u.user.id,
                "username": u.user.username,
                "nickname": u.user.nickname
            } if u.user else None,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in uploads
    ]

    return ResponseModel(
        code=200,
        message="获取成功",
        data=PaginatedResponse.create(
            items=data,
            total=total,
            page=pagination.page,
            size=pagination.size
        )
    )


@router.delete("/{upload_id}", response_model=ResponseModel[dict])
async def delete_upload(
    upload_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除上传的文件"""
    result = await db.execute(
        select(Upload).where(Upload.id == upload_id, Upload.user_id == current_user.id)
    )
    upload = result.scalar_one_or_none()
    
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在或无权删除"
        )
    
    # 删除物理文件
    try:
        if os.path.exists(upload.file_path):
            os.remove(upload.file_path)
    except Exception:
        pass
    
    # 删除数据库记录
    await db.delete(upload)
    await db.commit()
    
    return ResponseModel(code=200, message="删除成功", data={"id": upload_id})
