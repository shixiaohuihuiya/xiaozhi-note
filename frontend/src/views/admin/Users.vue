<template>
  <div>
    <h1>用户管理</h1>
    <div class="toolbar">
      <a-space>
        <a-button type="primary" @click="openCreateModal">
          <PlusOutlined /> 新增用户
        </a-button>
        <a-upload
          :show-upload-list="false"
          :before-upload="handleBatchUpload"
          accept=".xlsx"
        >
          <a-button>
            <UploadOutlined /> Excel 批量导入
          </a-button>
        </a-upload>
        <a-button @click="handleDownloadTemplate">
          <DownloadOutlined /> 下载模板
        </a-button>
      </a-space>
    </div>
    <a-table :columns="columns" :data-source="users" :loading="loading" :scroll="{ x: 800 }">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'role'">
          <a-tag :color="record.role === 2 ? 'purple' : (record.role === 1 ? 'red' : 'blue')">
            {{ record.role === 2 ? '超级管理员' : (record.role === 1 ? '管理员' : '普通用户') }}
          </a-tag>
        </template>
        <template v-if="column.key === 'status'">
          <a-tag :color="record.status === 1 ? 'success' : 'error'">
            {{ record.status === 1 ? '正常' : '禁用' }}
          </a-tag>
        </template>
        <template v-if="column.key === 'created_at'">
          {{ formatDateTime(record.created_at) }}
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="text" @click="openEditModal(record)">编辑</a-button>
            <a-button type="text" @click="toggleStatus(record)" :disabled="record.is_superadmin">
              {{ record.status === 1 ? '禁用' : '启用' }}
            </a-button>
            <a-button type="text" @click="showResetPassword(record)" :disabled="record.is_superadmin">
              重置密码
            </a-button>
            <a-button type="text" danger @click="handleDelete(record)" :disabled="record.is_superadmin">
              删除
            </a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 新增/编辑用户弹窗 -->
    <a-modal
      v-model:open="showModal"
      :title="isEdit ? '编辑用户' : '新增用户'"
      @ok="handleSave"
      @cancel="resetForm"
    >
      <a-form :model="form" :label-col="{ span: 4 }" :wrapper-col="{ span: 20 }">
        <a-form-item label="用户名" required>
          <a-input v-model:value="form.username" placeholder="3-50位字母数字下划线" />
        </a-form-item>
        <a-form-item label="邮箱" required>
          <a-input v-model:value="form.email" placeholder="请输入邮箱" />
        </a-form-item>
        <a-form-item label="密码" :required="!isEdit">
          <a-input-password
            v-model:value="form.password"
            :placeholder="isEdit ? '留空则不修改密码' : '6-32位密码'"
          />
        </a-form-item>
        <a-form-item label="昵称">
          <a-input v-model:value="form.nickname" placeholder="默认为用户名" />
        </a-form-item>
        <a-form-item label="角色">
          <a-select v-model:value="form.role" :options="roleOptions" />
        </a-form-item>
        <a-form-item label="状态" v-if="isEdit">
          <a-select v-model:value="form.status" :options="statusOptions" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, UploadOutlined, DownloadOutlined } from '@ant-design/icons-vue'
import {
  getAdminUsers,
  updateUserStatus,
  resetUserPassword,
  createUser,
  updateUser,
  deleteUser,
  batchCreateUsers,
  downloadUserTemplate
} from '@/api/admin'
import { formatDateTime } from '@/utils/date'

const loading = ref(false)
const users = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const showModal = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const form = ref({
  username: '',
  email: '',
  password: '',
  nickname: '',
  role: 0,
  status: 1
})

const roleOptions = [
  { label: '普通用户', value: 0 },
  { label: '管理员', value: 1 }
  // 超级管理员(role=2)只能通过系统初始化创建，不可手动分配
]

const statusOptions = [
  { label: '禁用', value: 0 },
  { label: '正常', value: 1 }
]

const columns = [
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '邮箱', dataIndex: 'email', key: 'email' },
  { title: '角色', dataIndex: 'role', key: 'role' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '注册时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action' }
]

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await getAdminUsers({
      page: page.value,
      size: pageSize.value
    })
    if (res.code === 200) {
      users.value = res.data.items
      total.value = res.data.total
    }
  } catch (error) {
    message.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const toggleStatus = async (record) => {
  try {
    const res = await updateUserStatus(record.id, record.status === 1 ? 0 : 1)
    if (res.code === 200) {
      message.success('操作成功')
      fetchUsers()
    }
  } catch (error) {
    message.error('操作失败')
  }
}

const showResetPassword = async (record) => {
  try {
    const res = await resetUserPassword(record.id)
    if (res.code === 200) {
      message.success(`密码重置成功，新密码为：${res.data.new_password}`)
    }
  } catch (error) {
    message.error('密码重置失败')
  }
}

const openCreateModal = () => {
  isEdit.value = false
  editingId.value = null
  resetForm()
  showModal.value = true
}

const openEditModal = (record) => {
  isEdit.value = true
  editingId.value = record.id
  form.value = {
    username: record.username,
    email: record.email,
    password: '',
    nickname: record.nickname || '',
    role: record.role,
    status: record.status
  }
  showModal.value = true
}

const resetForm = () => {
  form.value = {
    username: '',
    email: '',
    password: '',
    nickname: '',
    role: 0,
    status: 1
  }
}

const handleSave = async () => {
  if (!form.value.username || !form.value.email) {
    message.warning('请填写必填项')
    return
  }
  if (!isEdit.value && !form.value.password) {
    message.warning('请填写密码')
    return
  }
  try {
    const payload = {
      username: form.value.username,
      email: form.value.email,
      nickname: form.value.nickname || undefined,
      role: form.value.role,
      status: form.value.status
    }
    if (!isEdit.value) {
      payload.password = form.value.password
    }

    const res = isEdit.value
      ? await updateUser(editingId.value, payload)
      : await createUser(payload)

    if (res.code === 200) {
      message.success(isEdit.value ? '用户更新成功' : '用户创建成功')
      showModal.value = false
      resetForm()
      fetchUsers()
    }
  } catch (error) {
    message.error(error.message || (isEdit.value ? '更新失败' : '创建失败'))
  }
}

const handleDelete = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除用户 "${record.username}" 吗？此操作不可恢复！`,
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        const res = await deleteUser(record.id)
        if (res.code === 200) {
          message.success('用户删除成功')
          fetchUsers()
        }
      } catch (error) {
        message.error('删除失败')
      }
    }
  })
}

const handleBatchUpload = async (file) => {
  if (!file.name.endsWith('.xlsx')) {
    message.error('请上传 .xlsx 格式的 Excel 文件')
    return false
  }
  try {
    const res = await batchCreateUsers(file)
    if (res.code === 200) {
      const { success_count, failed_count, failed_rows } = res.data
      if (failed_count > 0) {
        message.warning(`导入完成：成功 ${success_count} 条，失败 ${failed_count} 条`)
        console.warn('导入失败明细：', failed_rows)
      } else {
        message.success(`成功导入 ${success_count} 位用户`)
      }
      fetchUsers()
    }
  } catch (error) {
    message.error(error.message || '批量导入失败')
  }
  return false
}

const handleDownloadTemplate = async () => {
  try {
    const res = await downloadUserTemplate()
    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '用户导入模板.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    message.success('模板下载成功')
  } catch (error) {
    message.error('模板下载失败')
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped lang="less">
.toolbar {
  margin-bottom: 16px;
}
</style>
