<template>
  <div>
    <h1>仪表盘</h1>
    <a-row :gutter="[16, 16]" class="stat-cards">
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card>
          <Statistic title="总用户数" :value="stats.total_users" />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card>
          <Statistic title="总笔记数" :value="stats.total_articles" />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card>
          <Statistic title="总评论数" :value="stats.total_comments" />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card>
          <Statistic title="总阅读量" :value="stats.total_views" />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card>
          <Statistic title="今日新增笔记" :value="stats.today_articles" />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card>
          <Statistic title="七日新增笔记" :value="stats.week_articles" />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card>
          <Statistic title="网站运行" :value="stats.site_uptime_days" suffix="天" />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card>
          <Statistic title="待审核笔记" :value="stats.pending_articles" />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card>
          <Statistic title="待审核评论" :value="stats.pending_comments" />
        </a-card>
      </a-col>
    </a-row>

    <!-- 七日笔记趋势 -->
    <a-row :gutter="[16, 16]" class="chart-row">
      <a-col :span="24">
        <a-card title="七日笔记发布趋势">
          <div class="bar-chart">
            <div
              v-for="item in dailyArticles"
              :key="item.date"
              class="bar-item"
            >
              <div class="bar-wrapper">
                <div
                  class="bar"
                  :style="{ height: getBarHeight(item.count) + '%' }"
                >
                  <span v-if="item.count > 0" class="bar-value">{{ item.count }}</span>
                </div>
              </div>
              <span class="bar-label">{{ item.date }}</span>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 今日新增笔记 -->
    <a-row :gutter="[16, 16]" class="list-row">
      <a-col :xs="24" :lg="12">
        <a-card
          title="今日新增笔记"
          :extra="todayArticles.length > 0 ? `${todayArticles.length} 篇` : '无'"
        >
          <a-list
            v-if="todayArticles.length > 0"
            :data-source="todayArticles"
            size="small"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #title>
                    <router-link :to="`/article/${item.id}`" target="_blank">
                      {{ item.title }}
                    </router-link>
                  </template>
                  <template #description>
                    <span>{{ item.author }} · {{ formatDateTime(item.created_at) }}</span>
                    <a-tag :color="item.status === 1 ? 'success' : 'default'" size="small" style="margin-left: 8px">
                      {{ item.status === 1 ? '已发布' : '草稿' }}
                    </a-tag>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
          <a-empty v-else description="今日暂无新增笔记" />
        </a-card>
      </a-col>
      <a-col :xs="24" :lg="12">
        <a-card
          title="待审核笔记"
          :extra="pendingArticles.length > 0 ? `${pendingArticles.length} 篇` : '无'"
        >
          <a-list
            v-if="pendingArticles.length > 0"
            :data-source="pendingArticles"
            size="small"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #title>
                    <router-link :to="`/article/${item.id}`" target="_blank">
                      {{ item.title }}
                    </router-link>
                  </template>
                  <template #description>
                    <span>{{ item.author }} · 更新于 {{ formatDateTime(item.updated_at) }}</span>
                    <a-button
                      type="primary"
                      size="small"
                      style="margin-left: 8px"
                      @click="$router.push(`/admin/articles?status=0`)"
                    >
                      去审核
                    </a-button>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
          <a-empty v-else description="暂无待审核笔记" />
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Statistic, message } from 'ant-design-vue'
import { getDashboardStats } from '@/api/admin'
import { formatDateTime } from '@/utils/date'

const stats = ref({
  total_users: 0,
  total_articles: 0,
  total_comments: 0,
  total_views: 0,
  today_articles: 0,
  week_articles: 0,
  site_uptime_days: 0,
  pending_comments: 0,
  pending_articles: 0
})

const dailyArticles = ref([])
const todayArticles = ref([])
const pendingArticles = ref([])

const fetchStats = async () => {
  try {
    const res = await getDashboardStats()
    if (res.code === 200) {
      stats.value = res.data.statistics
      dailyArticles.value = res.data.daily_articles || []
      todayArticles.value = res.data.today_articles_list || []
      pendingArticles.value = res.data.pending_articles_list || []
    }
  } catch (error) {
    message.error('获取统计数据失败')
    console.error(error)
  }
}

const maxDailyCount = ref(1)
const getBarHeight = (count) => {
  if (!count) return 4
  return Math.max(8, (count / maxDailyCount.value) * 100)
}

onMounted(async () => {
  await fetchStats()
  const counts = dailyArticles.value.map(d => d.count)
  maxDailyCount.value = counts.length > 0 ? Math.max(...counts, 1) : 1
})
</script>

<style scoped lang="less">
.stat-cards {
  margin-top: 24px;

  :deep(.ant-card) {
    background: var(--card-bg);
    border-color: var(--border-color);
  }

  :deep(.ant-statistic-title) {
    color: var(--text-secondary);
  }

  :deep(.ant-statistic-content) {
    color: var(--text-primary);
  }
}

.chart-row,
.list-row {
  margin-top: 16px;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 200px;
  padding: 16px 0;

  .bar-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    max-width: 80px;

    .bar-wrapper {
      width: 100%;
      height: 160px;
      display: flex;
      align-items: flex-end;
      justify-content: center;

      .bar {
        width: 32px;
        background: var(--ant-primary-color);
        border-radius: 4px 4px 0 0;
        transition: height 0.5s ease;
        position: relative;
        min-height: 4px;

        .bar-value {
          position: absolute;
          top: -20px;
          left: 50%;
          transform: translateX(-50%);
          font-size: 12px;
          color: var(--text-primary);
          white-space: nowrap;
        }
      }
    }

    .bar-label {
      margin-top: 8px;
      font-size: 12px;
      color: var(--text-secondary);
    }
  }
}

:deep(.ant-list-item-meta-title a) {
  color: var(--ant-primary-color);
}

:deep(.ant-list-item-meta-title) {
  color: var(--text-primary);
}

:deep(.ant-list-item-meta-description) {
  color: var(--text-secondary);
}

:deep(.ant-card-head-title) {
  color: var(--text-primary);
}

:deep(.ant-card-extra) {
  color: var(--text-secondary);
}

:deep(.ant-empty-description) {
  color: var(--text-secondary);
}

.list-row {
  :deep(.ant-card) {
    background: var(--card-bg);
    border-color: var(--border-color);
  }
}
</style>
