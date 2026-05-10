<template>
  <div class="page-container">
    <a-card title="个人中心" class="profile-card">
      <div class="profile-content">
        <div class="avatar-section">
          <a-upload
            :show-upload-list="false"
            :before-upload="beforeAvatarUpload"
            :custom-request="handleAvatarUpload"
            accept="image/*"
          >
            <div class="avatar-wrapper">
              <a-avatar :size="100" :src="form.avatar" class="profile-avatar">
                {{ form.nickname?.[0] || form.username?.[0] }}
              </a-avatar>
              <div class="avatar-mask">
                <CameraOutlined />
                <span>更换头像</span>
              </div>
            </div>
          </a-upload>
        </div>

        <a-form :model="form" layout="vertical" class="profile-form">
          <a-form-item label="用户名">
            <span class="static-text">{{ form.username }}</span>
          </a-form-item>
          <a-form-item label="邮箱">
            <span class="static-text">{{ form.email }}</span>
          </a-form-item>
          <a-form-item label="昵称">
            <a-input v-model:value="form.nickname" placeholder="请输入昵称" />
          </a-form-item>
          <a-form-item label="简介">
            <a-textarea v-model:value="form.bio" :rows="4" placeholder="介绍一下自己..." />
          </a-form-item>
          <a-form-item>
            <a-button type="primary" :loading="saving" @click="saveProfile">保存修改</a-button>
          </a-form-item>
        </a-form>
      </div>
    </a-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { CameraOutlined } from '@ant-design/icons-vue'
import { useUserStore } from '@/stores/user'
import { updateCurrentUser } from '@/api/user'
import { uploadImage } from '@/api/upload'

const userStore = useUserStore()
const saving = ref(false)
const avatarUploading = ref(false)

const form = reactive({
  username: '',
  email: '',
  nickname: '',
  bio: '',
  avatar: ''
})

const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    message.error('只能上传图片文件')
    return false
  }
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    message.error('图片大小不能超过 2MB')
    return false
  }
  return true
}

const handleAvatarUpload = async ({ file }) => {
  avatarUploading.value = true
  try {
    const res = await uploadImage(file, 3)
    if (res.code === 200) {
      form.avatar = res.data.url
      message.success('头像上传成功')
    }
  } catch (error) {
    message.error('头像上传失败')
  } finally {
    avatarUploading.value = false
  }
}

const saveProfile = async () => {
  saving.value = true
  try {
    const res = await updateCurrentUser({
      nickname: form.nickname,
      bio: form.bio,
      avatar: form.avatar
    })
    if (res.code === 200) {
      message.success('保存成功')
      userStore.userInfo = { ...userStore.userInfo, ...res.data }
    }
  } catch (error) {
    message.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  if (userStore.userInfo) {
    Object.assign(form, userStore.userInfo)
  }
})
</script>

<style scoped lang="less">
.page-container {
  min-height: calc(100vh - 64px - 70px);
  background: var(--bg-primary);
  padding: 24px;
}

.profile-card {
  max-width: 600px;
  margin: 0 auto;
  background: var(--card-bg);
  border-color: var(--border-color);

  :deep(.ant-card-head) {
    border-bottom-color: var(--border-color);
    text-align: center;
  }

  :deep(.ant-card-head-title) {
    color: var(--text-primary);
    font-size: 20px;
    font-weight: 600;
  }
}

.profile-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-section {
  margin-bottom: 24px;
}

.avatar-wrapper {
  position: relative;
  cursor: pointer;
  border-radius: 50%;
  overflow: hidden;

  .profile-avatar {
    display: block;
    transition: filter 0.2s;
  }

  .avatar-mask {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.5);
    color: #fff;
    font-size: 12px;
    opacity: 0;
    transition: opacity 0.2s;

    .anticon {
      font-size: 20px;
      margin-bottom: 4px;
    }
  }

  &:hover {
    .profile-avatar {
      filter: blur(2px);
    }

    .avatar-mask {
      opacity: 1;
    }
  }
}

.profile-form {
  width: 100%;
  max-width: 400px;

  :deep(.ant-form-item-label > label) {
    color: var(--text-primary);
  }

  :deep(.ant-input),
  :deep(.ant-input-textarea) {
    background: var(--bg-primary);
    border-color: var(--border-color);
    color: var(--text-primary);
  }

  .static-text {
    color: var(--text-secondary);
  }

  :deep(.ant-btn-primary) {
    width: 100%;
  }
}
</style>
