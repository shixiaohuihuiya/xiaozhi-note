<template>
  <div class="not-found-wrapper">
    <div class="not-found">
      <a-result
        status="404"
        title="404"
        sub-title="抱歉，您访问的页面不存在"
      >
        <template #extra>
          <a-button type="primary" @click="$router.push('/')">返回首页</a-button>
        </template>
      </a-result>
    </div>
  </div>
</template>

<style scoped lang="less">
.not-found-wrapper {
  // Reset to remove any page-container padding and constraints
  margin: -24px;
  padding: 0;
  width: calc(100% + 48px);
  min-height: calc(100vh - 64px - 70px);
  display: flex;
  align-items: center;
  justify-content: center;
  // Override the grid background
  background: transparent !important;
}

.not-found {
  width: 100%;
  max-width: 600px;
  padding: 40px 24px;
  
  :deep(.ant-result) {
    width: 100%;
    max-width: 500px;
    margin: 0 auto;
    
    .ant-result-title {
      color: var(--text-primary) !important;
    }
    
    .ant-result-subtitle {
      color: var(--text-secondary) !important;
    }
  }
}
</style>
