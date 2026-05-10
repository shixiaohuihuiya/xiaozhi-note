<template>
  <div>
    <h1>AI配置管理</h1>
    <a-card title="豆包AI设置">
      <a-form
        :model="form"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
        layout="horizontal"
      >
        <a-form-item label="启用AI功能">
          <a-switch v-model:checked="form.enabled" />
        </a-form-item>

        <a-form-item label="API Key">
          <a-input-password
            v-model:value="form.apiKey"
            placeholder="输入新的 API Key（留空则保持不变）"
            style="width: 100%"
          />
          <div class="hint">当前：{{ config.api_key || '未配置' }}</div>
        </a-form-item>

        <a-form-item label="模型">
          <a-input v-model:value="form.model" placeholder="如：doubao-pro-32k" />
        </a-form-item>

        <a-form-item label="轻量模型">
          <a-input v-model:value="form.liteModel" placeholder="如：doubao-lite-32k" />
        </a-form-item>

        <a-form-item label="Base URL">
          <a-input v-model:value="form.baseUrl" placeholder="https://ark.cn-beijing.volces.com/api/v3" />
        </a-form-item>

        <a-form-item label="单次最大Token">
          <a-input-number v-model:value="form.maxTokens" :min="500" :max="8000" style="width: 100%" />
        </a-form-item>

        <a-form-item label="每日用户限额">
          <a-input-number v-model:value="form.dailyLimit" :min="1" :max="1000" style="width: 100%" />
        </a-form-item>

        <a-form-item :wrapper-col="{ offset: 6, span: 16 }">
          <a-button type="primary" :loading="saving" @click="saveConfig">保存配置</a-button>
          <a-button style="margin-left: 12px" @click="fetchConfig">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getAiConfig, updateAiConfig } from '@/api/admin'

const saving = ref(false)
const config = ref({})

const form = reactive({
  enabled: true,
  apiKey: '',
  model: 'doubao-pro-32k',
  liteModel: 'doubao-lite-32k',
  baseUrl: 'https://ark.cn-beijing.volces.com/api/v3',
  maxTokens: 4000,
  dailyLimit: 100
})

const fetchConfig = async () => {
  try {
    const res = await getAiConfig()
    if (res.code === 200) {
      const data = res.data
      config.value = data
      form.enabled = data.enabled ?? true
      form.model = data.model || 'doubao-pro-32k'
      form.liteModel = data.lite_model || 'doubao-lite-32k'
      form.baseUrl = data.base_url || 'https://ark.cn-beijing.volces.com/api/v3'
      form.maxTokens = data.max_tokens || 4000
      form.dailyLimit = data.daily_limit || 100
      form.apiKey = ''
    }
  } catch (error) {
    message.error('获取AI配置失败')
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    const payload = {
      enabled: form.enabled,
      model: form.model,
      lite_model: form.liteModel,
      base_url: form.baseUrl,
      max_tokens: form.maxTokens,
      daily_limit: form.dailyLimit
    }
    if (form.apiKey && !form.apiKey.includes('****')) {
      payload.api_key = form.apiKey
    }
    const res = await updateAiConfig(payload)
    if (res.code === 200) {
      message.success('配置已保存')
      form.apiKey = ''
      fetchConfig()
    }
  } catch (error) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchConfig()
})
</script>

<style scoped lang="less">
.hint {
  color: var(--text-tertiary);
  font-size: 12px;
  margin-top: 4px;
}
</style>
