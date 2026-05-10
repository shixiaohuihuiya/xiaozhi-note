<template>
  <div>
    <h1>分类管理</h1>
    <div class="toolbar">
      <a-button type="primary" @click="resetForm(); showModal = true">新增分类</a-button>
    </div>
    <a-table :columns="columns" :data-source="categories" :loading="loading" :scroll="{ x: 800 }">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="text" @click="editCategory(record)">编辑</a-button>
            <a-button type="text" danger @click="deleteCategory(record)">删除</a-button>
          </a-space>
        </template>
      </template>
    </a-table>
    
    <a-modal v-model:open="showModal" title="分类" @ok="saveCategory" @cancel="resetForm">
      <a-form :model="form" :label-col="{ span: 4 }" :wrapper-col="{ span: 20 }">
        <a-form-item label="名称">
          <a-input v-model:value="form.name" />
        </a-form-item>
        <a-form-item label="标识">
          <a-input v-model:value="form.slug" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="form.description" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getCategories, createCategory, updateCategory, deleteCategory as deleteCategoryApi } from '@/api/category'

const loading = ref(false)
const showModal = ref(false)
const categories = ref([])
const isEdit = ref(false)

const form = reactive({
  id: null,
  name: '',
  slug: '',
  description: ''
})

const columns = [
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '标识', dataIndex: 'slug', key: 'slug' },
  { title: '笔记数', dataIndex: 'article_count', key: 'article_count' },
  { title: '操作', key: 'action' }
]

const fetchCategories = async () => {
  loading.value = true
  try {
    const res = await getCategories()
    if (res.code === 200) {
      categories.value = res.data
    }
  } catch (error) {
    message.error('获取分类失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.id = null
  form.name = ''
  form.slug = ''
  form.description = ''
  isEdit.value = false
}

const editCategory = (record) => {
  Object.assign(form, record)
  isEdit.value = true
  showModal.value = true
}

const deleteCategory = async (record) => {
  try {
    const res = await deleteCategoryApi(record.id)
    if (res.code === 200) {
      message.success('删除成功')
      fetchCategories()
    }
  } catch (error) {
    message.error('删除失败')
  }
}

const saveCategory = async () => {
  try {
    let res
    if (isEdit.value) {
      res = await updateCategory(form.id, form)
    } else {
      res = await createCategory(form)
    }
    
    if (res.code === 200) {
      message.success(isEdit.value ? '更新成功' : '创建成功')
      showModal.value = false
      resetForm()
      fetchCategories()
    }
  } catch (error) {
    message.error('保存失败')
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped lang="less">
.toolbar {
  margin-bottom: 16px;
}
</style>
