<template>
  <div class="page-container">
    <h1>笔记标签</h1>
    <div class="tag-cloud">
      <a-tag
        v-for="tag in tags"
        :key="tag.id"
        :color="tag.color"
        class="tag-item"
        @click="goToTag(tag.id)"
      >
        {{ tag.name }} ({{ tag.article_count }})
      </a-tag>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getTags } from '@/api/tag'

const router = useRouter()
const tags = ref([])
const loading = ref(false)

const fetchTags = async () => {
  loading.value = true
  try {
    const res = await getTags()
    if (res.code === 200) {
      tags.value = res.data.items || []
    }
  } catch (error) {
    message.error('获取标签失败')
  } finally {
    loading.value = false
  }
}

const goToTag = (id) => {
  router.push(`/articles?tag=${id}`)
}

onMounted(() => {
  fetchTags()
})
</script>

<style scoped lang="less">
h1 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  
  .tag-item {
    font-size: 14px;
    padding: 4px 12px;
    cursor: pointer;
    
    &:hover {
      opacity: 0.8;
    }
  }
}
</style>
