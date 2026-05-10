<template>
  <div class="page-container">
    <h1>笔记分类</h1>
    <div class="category-grid">
      <div class="category-card" v-for="cat in categories" :key="cat.id" @click="goToCategory(cat.id)">
        <FolderOutlined style="font-size: 48px; color: var(--ant-primary-color)" />
        <h3>{{ cat.name }}</h3>
        <p>{{ cat.article_count }} 篇笔记</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { FolderOutlined } from '@ant-design/icons-vue'
import { getCategories } from '@/api/category'

const router = useRouter()
const categories = ref([])
const loading = ref(false)

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

const goToCategory = (id) => {
  router.push(`/articles?category=${id}`)
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped lang="less">
h1 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;

  @media (max-width: 992px) {
    grid-template-columns: repeat(3, 1fr);
  }

  @media (max-width: 576px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.category-card {
  background: var(--card-bg, #fff);
  border: 1px solid var(--border-color, #f0f0f0);
  border-radius: 8px;
  text-align: center;
  padding: 32px 24px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }

  h3 {
    margin: 16px 0 8px;
    font-size: 16px;
    font-weight: 500;
    color: var(--text-primary);
  }

  p {
    color: var(--text-secondary);
    margin: 0;
  }
}
</style>
