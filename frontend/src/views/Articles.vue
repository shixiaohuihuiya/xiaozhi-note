<template>
  <div class="page-container">
    <div class="page-header">
      <h1>{{ filterTitle }}</h1>
      <a-input-search
        v-model:value="searchKeyword"
        placeholder="搜索笔记..."
        style="width: 300px"
        @search="handleSearch"
      />
    </div>

    <div v-if="tagId || categoryId" class="filter-bar">
      <a-tag v-if="tagId" color="blue" closable @close="clearFilter">
        <TagOutlined /> 标签筛选
      </a-tag>
      <a-tag v-if="categoryId" color="green" closable @close="clearFilter">
        <FolderOutlined /> 分类筛选
      </a-tag>
      <a-button type="link" size="small" @click="clearFilter">清除筛选</a-button>
    </div>
    
    <div class="article-list">
      <a-card
        v-for="article in articles"
        :key="article.id"
        class="article-item card"
        hoverable
        @click="goToArticle(article.slug)"
      >
        <div class="article-body">
          <div class="article-content">
            <h3 class="article-title">{{ article.title }}</h3>
            <p class="article-summary">{{ article.summary }}</p>
            <div class="article-meta">
              <span><UserOutlined /> {{ article.author?.nickname || article.author?.username }}</span>
              <span><FolderOutlined /> {{ article.category?.name || '未分类' }}</span>
              <span><EyeOutlined /> {{ article.view_count }}</span>
              <span><LikeOutlined /> {{ article.like_count }}</span>
              <span><CommentOutlined /> {{ article.comment_count }}</span>
            </div>
          </div>
          <div class="article-cover" v-if="article.cover_image">
            <img :src="article.cover_image" :alt="article.title" />
          </div>
        </div>
      </a-card>
    </div>
    
    <div class="pagination">
      <a-pagination
        v-model:current="page"
        :total="total"
        :page-size="pageSize"
        show-total
        @change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, FolderOutlined, EyeOutlined, LikeOutlined, CommentOutlined, TagOutlined } from '@ant-design/icons-vue'
import { getArticles } from '@/api/article'

const route = useRoute()
const router = useRouter()

const articles = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const tagId = ref(null)
const categoryId = ref(null)
const filterTitle = ref('笔记列表')

const fetchArticles = async () => {
  try {
    const params = {
      page: page.value,
      size: pageSize.value,
      keyword: searchKeyword.value || undefined
    }
    if (tagId.value) {
      params.tag_id = tagId.value
    }
    if (categoryId.value) {
      params.category_id = categoryId.value
    }
    const res = await getArticles(params)
    if (res.code === 200) {
      articles.value = res.data.items
      total.value = res.data.total
    }
  } catch (error) {
    message.error('获取笔记失败')
  }
}

const handleSearch = () => {
  page.value = 1
  fetchArticles()
}

const clearFilter = () => {
  tagId.value = null
  categoryId.value = null
  filterTitle.value = '笔记列表'
  searchKeyword.value = ''
  page.value = 1
  // Remove query params from URL
  router.replace({ path: '/articles', query: {} })
  fetchArticles()
}

const applyRouteQuery = () => {
  const query = route.query
  if (query.tag) {
    tagId.value = Number(query.tag)
    categoryId.value = null
    filterTitle.value = '标签笔记'
  } else if (query.category) {
    categoryId.value = Number(query.category)
    tagId.value = null
    filterTitle.value = '分类笔记'
  } else {
    tagId.value = null
    categoryId.value = null
    filterTitle.value = '笔记列表'
  }
  page.value = 1
  fetchArticles()
}

watch(() => route.query, () => {
  applyRouteQuery()
}, { deep: true })

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchArticles()
}

const goToArticle = (slug) => {
  router.push(`/article/${slug}`)
}

onMounted(() => {
  applyRouteQuery()
})
</script>

<style scoped lang="less">
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h1 {
    font-size: 24px;
    font-weight: 600;
  }
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border-radius: 6px;
}

.article-item {
  margin-bottom: 16px;
  cursor: pointer;
  overflow: hidden;

  .article-body {
    display: flex;
    gap: 16px;
    align-items: stretch;

    .article-content {
      flex: 1;
      min-width: 0;
    }

    .article-cover {
      width: 240px;
      min-width: 240px;
      height: 150px;
      overflow: hidden;
      border-radius: 8px;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s ease;
      }
    }
  }

  &:hover .article-cover img {
    transform: scale(1.03);
  }

  .article-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 8px;
    color: var(--text-primary);
  }

  .article-summary {
    color: var(--text-secondary);
    margin-bottom: 12px;
    line-height: 1.6;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .article-meta {
    display: flex;
    gap: 16px;
    color: var(--text-tertiary);
    font-size: 13px;
    flex-wrap: wrap;
  }
}

.pagination {
  text-align: center;
  margin-top: 32px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;

    h1 {
      text-align: center;
    }

    // Make search input full width on mobile to match article cards
    :deep(.ant-input-search) {
      width: 100% !important;
    }
  }

  .article-item .article-body {
    flex-direction: column;

    .article-cover {
      width: 100%;
      height: 180px;
      order: -1;
    }
  }

  .article-meta {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>
