<template>
  <div>
    <h1>标签管理</h1>
    <div class="toolbar">
      <a-button type="primary" @click="resetForm(); showModal = true">新增标签</a-button>
    </div>
    <a-table
      :columns="columns"
      :data-source="tags"
      :loading="loading"
      :pagination="pagination"
      @change="handleTableChange"
      :scroll="{ x: 800 }"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'color'">
          <span class="color-dot" :style="{ background: record.color }"></span>
          {{ record.color }}
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="text" @click="editTag(record)">编辑</a-button>
            <a-button type="text" danger @click="deleteTag(record)">删除</a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="showModal" :title="isEdit ? '编辑标签' : '新增标签'" @ok="saveTag" @cancel="resetForm">
      <a-form :model="form" :label-col="{ span: 4 }" :wrapper-col="{ span: 20 }">
        <a-form-item label="名称">
          <a-input v-model:value="form.name" placeholder="标签名称" />
        </a-form-item>
        <a-form-item label="标识">
          <a-input v-model:value="form.slug" placeholder="英文标识，如 python" />
        </a-form-item>
        <a-form-item label="颜色">
          <a-input v-model:value="form.color" type="color" style="width: 60px; padding: 2px;" />
          <a-input v-model:value="form.color" placeholder="#1890ff" style="width: 200px; margin-left: 8px;" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { getAdminTags, createTag, updateTag, deleteTag as deleteTagApi } from '@/api/admin'

const loading = ref(false)
const showModal = ref(false)
const tags = ref([])
const isEdit = ref(false)
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true
})

const form = reactive({
  id: null,
  name: '',
  slug: '',
  color: '#1890ff'
})

const columns = [
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '标识', dataIndex: 'slug', key: 'slug' },
  { title: '颜色', key: 'color' },
  { title: '笔记数', dataIndex: 'article_count', key: 'article_count' },
  { title: '操作', key: 'action' }
]

const fetchTags = async () => {
  loading.value = true
  try {
    const res = await getAdminTags({
      page: pagination.current,
      size: pagination.pageSize,
      sort: 'name'
    })
    if (res.code === 200) {
      tags.value = res.data.items || []
      pagination.total = res.data.total || 0
    }
  } catch (error) {
    message.error('获取标签失败')
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchTags()
}

const resetForm = () => {
  form.id = null
  form.name = ''
  form.slug = ''
  form.color = '#1890ff'
  isEdit.value = false
}

const editTag = (record) => {
  Object.assign(form, record)
  isEdit.value = true
  showModal.value = true
}

const deleteTag = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除标签「${record.name}」吗？`,
    okText: '删除',
    okType: 'danger',
    onOk: async () => {
      try {
        const res = await deleteTagApi(record.id)
        if (res.code === 200) {
          message.success('删除成功')
          fetchTags()
        }
      } catch (error) {
        message.error('删除失败')
      }
    }
  })
}

const saveTag = async () => {
  try {
    let res
    if (isEdit.value) {
      res = await updateTag(form.id, { name: form.name, slug: form.slug, color: form.color })
    } else {
      res = await createTag({ name: form.name, slug: form.slug, color: form.color })
    }

    if (res.code === 200) {
      message.success(isEdit.value ? '更新成功' : '创建成功')
      showModal.value = false
      resetForm()
      fetchTags()
    }
  } catch (error) {
    message.error('保存失败')
  }
}

onMounted(() => {
  fetchTags()
})
</script>

<style scoped lang="less">
.toolbar {
  margin-bottom: 16px;
}
.color-dot {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 4px;
  margin-right: 8px;
  vertical-align: middle;
}
</style>
