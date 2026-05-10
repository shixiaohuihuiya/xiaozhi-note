<template>
  <div class="page-container">
    <a-card :title="isForce ? '设置新密码' : '修改密码'" class="password-card" :body-style="{ paddingTop: '32px', paddingBottom: '32px' }">
      <a-alert
        v-if="isForce"
        message="管理员已重置您的密码"
        description="为了账号安全，请设置一个新的密码。"
        type="warning"
        show-icon
        style="margin-bottom: 24px;"
      />
      <a-form :model="pwdForm" :label-col="{ span: 4 }" :wrapper-col="{ span: 16 }">
        <a-form-item v-if="!isForce" label="当前密码" name="old_password">
          <a-input-password v-model:value="pwdForm.old_password" placeholder="请输入当前密码" />
        </a-form-item>
        <a-form-item label="新密码" name="new_password">
          <a-input-password v-model:value="pwdForm.new_password" placeholder="请输入新密码" />
        </a-form-item>
        <a-form-item label="确认密码" name="confirm_password">
          <a-input-password v-model:value="pwdForm.confirm_password" placeholder="请再次输入新密码" />
        </a-form-item>
        <a-form-item :wrapper-col="{ offset: 4, span: 16 }">
          <a-button type="primary" :loading="pwdSaving" @click="changePassword">
            {{ isForce ? '确认设置' : '修改密码' }}
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { updatePassword } from '@/api/user'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isForce = computed(() => route.query.force === '1')
const pwdSaving = ref(false)

const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const changePassword = async () => {
  if (!isForce.value && !pwdForm.old_password) {
    message.warning('请输入当前密码')
    return
  }
  if (!pwdForm.new_password || !pwdForm.confirm_password) {
    message.warning('请填写所有密码字段')
    return
  }
  if (pwdForm.new_password !== pwdForm.confirm_password) {
    message.warning('两次输入的新密码不一致')
    return
  }
  if (pwdForm.new_password.length < 6) {
    message.warning('新密码长度不能少于6位')
    return
  }

  pwdSaving.value = true
  try {
    const payload = { new_password: pwdForm.new_password }
    if (!isForce.value) {
      payload.old_password = pwdForm.old_password
    }
    const res = await updatePassword(payload)
    if (res.code === 200) {
      message.success('密码修改成功')
      pwdForm.old_password = ''
      pwdForm.new_password = ''
      pwdForm.confirm_password = ''
      // 清除强制修改标记
      if (userStore.userInfo) {
        userStore.userInfo.must_change_password = false
        localStorage.setItem('userInfo', JSON.stringify(userStore.userInfo))
      }
      if (isForce.value) {
        router.push('/')
      }
    }
  } catch (error) {
    message.error(error.message || '密码修改失败')
  } finally {
    pwdSaving.value = false
  }
}
</script>

<style scoped lang="less">
.page-container {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.password-card {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}
</style>
