<template>
  <div class="register-page">
    <!-- 左侧区域 -->
    <div class="register-left">
      <div class="tech-bg">
        <div class="grid-lines"></div>
        <div class="scan-line"></div>
        <div class="glow-circle"></div>
        <div class="glow-circle-2"></div>
        <div class="glow-circle-3"></div>
        <div class="tech-ring"></div>
        <div class="tech-ring-2"></div>
        <div class="particles">
          <span v-for="n in 30" :key="n" :class="'particle p' + n"></span>
        </div>
        <div class="data-stream">
          <span v-for="n in 15" :key="'s' + n" :class="'stream s' + n">{{ ['01','10','XZ','AI','<>','{}','//','**','++','&&','||','==','=>','[]',';;'][n-1] }}</span>
        </div>
      </div>
      <div class="left-content">
        <div class="brand-logo">XZ</div>
        <h1>创建你的免费账号</h1>
        <p class="left-desc">加入小智笔记，开启智能写作之旅</p>
        <div class="feature-list">
          <div class="feature-item">
            <span class="feature-dot"></span>
            <span>AI 智能辅助写作</span>
          </div>
          <div class="feature-item">
            <span class="feature-dot"></span>
            <span>Markdown 实时预览</span>
          </div>
          <div class="feature-item">
            <span class="feature-dot"></span>
            <span>多主题自由切换</span>
          </div>
          <div class="feature-item">
            <span class="feature-dot"></span>
            <span>云端数据同步</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧区域 -->
    <div class="register-right">
      <div class="right-header">
        <span>已有账号？</span>
        <a @click="$router.push('/login')">立即登录 →</a>
      </div>

      <div class="right-form">
        <h2>注册小智笔记</h2>

        <a-form
          :model="formState"
          :rules="rules"
          @finish="handleSubmit"
          class="auth-form"
          layout="vertical"
        >
          <a-form-item label="用户名" name="username">
            <a-input
              v-model:value="formState.username"
              placeholder="请输入用户名"
              size="large"
            />
          </a-form-item>

          <a-form-item label="邮箱" name="email">
            <a-input
              v-model:value="formState.email"
              placeholder="请输入邮箱"
              size="large"
            />
          </a-form-item>

          <a-form-item label="密码" name="password">
            <a-input-password
              v-model:value="formState.password"
              placeholder="请输入密码"
              size="large"
            />
          </a-form-item>

          <a-form-item label="确认密码" name="confirmPassword">
            <a-input-password
              v-model:value="formState.confirmPassword"
              placeholder="请再次输入密码"
              size="large"
            />
          </a-form-item>

          <a-form-item label="验证码" name="captcha_code">
            <div class="captcha-row">
              <a-input
                v-model:value="formState.captcha_code"
                placeholder="请输入验证码"
                size="large"
                style="flex: 1;"
              />
              <img
                v-if="captchaImage"
                :src="captchaImage"
                class="captcha-img"
                @click="refreshCaptcha"
                title="点击刷新"
              />
            </div>
          </a-form-item>

          <a-form-item>
            <a-button
              type="primary"
              html-type="submit"
              size="large"
              block
              :loading="loading"
            >
              创建账号
            </a-button>
          </a-form-item>
        </a-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons-vue'
import { useUserStore } from '@/stores/user'
import { getCaptcha } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const captchaImage = ref('')
const captchaKey = ref('')

const formState = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  captcha_code: ''
})

const validateConfirmPassword = (rule, value) => {
  if (value !== formState.password) {
    return Promise.reject('两次输入的密码不一致')
  }
  return Promise.resolve()
}

const rules = {
  username: [
    { required: true, message: '请输入用户名' },
    { min: 3, message: '用户名至少3个字符' }
  ],
  email: [
    { required: true, message: '请输入邮箱' },
    { type: 'email', message: '请输入有效的邮箱地址' }
  ],
  password: [
    { required: true, message: '请输入密码' },
    { min: 6, message: '密码至少6个字符' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码' },
    { validator: validateConfirmPassword }
  ],
  captcha_code: [
    { required: true, message: '请输入验证码' }
  ]
}

const refreshCaptcha = async () => {
  try {
    const res = await getCaptcha()
    if (res.code === 200) {
      captchaKey.value = res.data.key
      captchaImage.value = res.data.image
    }
  } catch (error) {
    console.error('获取验证码失败:', error)
  }
}

const handleSubmit = async () => {
  loading.value = true
  try {
    const res = await userStore.register({
      username: formState.username,
      email: formState.email,
      password: formState.password,
      captcha_key: captchaKey.value,
      captcha_code: formState.captcha_code
    })
    if (res.code === 200) {
      message.success('注册成功，请登录')
      router.push('/login')
    }
  } catch (error) {
    message.error(error.message || '注册失败')
    refreshCaptcha()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshCaptcha()
})
</script>

<style scoped lang="less">
.register-page {
  min-height: 100vh;
  display: flex;

  @media (max-width: 768px) {
    flex-direction: column;
  }
}

// 左侧区域
.register-left {
  flex: 1;
  background: linear-gradient(135deg, var(--ant-primary-color) 0%, var(--ant-primary-color-hover) 100%);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
  position: relative;
  overflow: hidden;

  @media (max-width: 768px) {
    padding: 32px 24px;
    min-height: 300px;
  }

  .tech-bg {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;

    .grid-lines {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-image:
        linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px);
      background-size: 50px 50px;
    }

    .glow-circle {
      position: absolute;
      width: 400px;
      height: 400px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
      top: -100px;
      right: -100px;
      animation: float 8s ease-in-out infinite;
    }

    .glow-circle-2 {
      position: absolute;
      width: 300px;
      height: 300px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
      bottom: -50px;
      left: -50px;
      animation: float 10s ease-in-out infinite reverse;
    }

    .particles {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;

      .particle {
        position: absolute;
        width: 3px;
        height: 3px;
        background: rgba(255,255,255,0.6);
        border-radius: 50%;
        box-shadow: 0 0 6px rgba(255,255,255,0.4);
        animation: particle-float 12s linear infinite;

        &.p1 { left: 5%; animation-delay: 0s; }
        &.p2 { left: 10%; animation-delay: 0.4s; }
        &.p3 { left: 15%; animation-delay: 0.8s; }
        &.p4 { left: 20%; animation-delay: 1.2s; }
        &.p5 { left: 25%; animation-delay: 1.6s; }
        &.p6 { left: 30%; animation-delay: 2s; }
        &.p7 { left: 35%; animation-delay: 2.4s; }
        &.p8 { left: 40%; animation-delay: 2.8s; }
        &.p9 { left: 45%; animation-delay: 3.2s; }
        &.p10 { left: 50%; animation-delay: 3.6s; }
        &.p11 { left: 55%; animation-delay: 4s; }
        &.p12 { left: 60%; animation-delay: 4.4s; }
        &.p13 { left: 65%; animation-delay: 4.8s; }
        &.p14 { left: 70%; animation-delay: 5.2s; }
        &.p15 { left: 75%; animation-delay: 5.6s; }
        &.p16 { left: 80%; animation-delay: 6s; }
        &.p17 { left: 85%; animation-delay: 6.4s; }
        &.p18 { left: 90%; animation-delay: 6.8s; }
        &.p19 { left: 95%; animation-delay: 7.2s; }
        &.p20 { left: 8%; animation-delay: 7.6s; }
        &.p21 { left: 18%; animation-delay: 8s; }
        &.p22 { left: 28%; animation-delay: 8.4s; }
        &.p23 { left: 38%; animation-delay: 8.8s; }
        &.p24 { left: 48%; animation-delay: 9.2s; }
        &.p25 { left: 58%; animation-delay: 9.6s; }
        &.p26 { left: 68%; animation-delay: 10s; }
        &.p27 { left: 78%; animation-delay: 10.4s; }
        &.p28 { left: 88%; animation-delay: 10.8s; }
        &.p29 { left: 98%; animation-delay: 11.2s; }
        &.p30 { left: 3%; animation-delay: 11.6s; }
      }
    }

    // 扫描线
    .scan-line {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
      animation: scan 4s ease-in-out infinite;
    }

    @keyframes scan {
      0%, 100% { top: 0; opacity: 0; }
      10% { opacity: 1; }
      90% { opacity: 1; }
      100% { top: 100%; opacity: 0; }
    }

    // 数据流
    .data-stream {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      font-family: 'Courier New', monospace;
      font-size: 12px;
      color: rgba(255,255,255,0.15);
      overflow: hidden;
      pointer-events: none;

      .stream {
        position: absolute;
        animation: stream-float 8s linear infinite;

        &.s1 { left: 8%; top: 20%; animation-delay: 0s; }
        &.s2 { left: 22%; top: 60%; animation-delay: 1s; }
        &.s3 { left: 38%; top: 30%; animation-delay: 2s; }
        &.s4 { left: 52%; top: 70%; animation-delay: 3s; }
        &.s5 { left: 68%; top: 40%; animation-delay: 4s; }
        &.s6 { left: 82%; top: 80%; animation-delay: 5s; }
        &.s7 { left: 15%; top: 50%; animation-delay: 6s; }
        &.s8 { left: 45%; top: 10%; animation-delay: 7s; }
        &.s9 { left: 75%; top: 55%; animation-delay: 0.5s; }
        &.s10 { left: 30%; top: 85%; animation-delay: 1.5s; }
        &.s11 { left: 60%; top: 25%; animation-delay: 2.5s; }
        &.s12 { left: 90%; top: 65%; animation-delay: 3.5s; }
        &.s13 { left: 5%; top: 75%; animation-delay: 4.5s; }
        &.s14 { left: 35%; top: 45%; animation-delay: 5.5s; }
        &.s15 { left: 55%; top: 90%; animation-delay: 6.5s; }
      }
    }

    @keyframes stream-float {
      0% { transform: translateY(0) rotate(0deg); opacity: 0; }
      20% { opacity: 0.3; }
      80% { opacity: 0.3; }
      100% { transform: translateY(-100px) rotate(10deg); opacity: 0; }
    }

    // 科技圆环
    .tech-ring {
      position: absolute;
      width: 200px;
      height: 200px;
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 50%;
      top: 30%;
      left: -50px;
      animation: ring-rotate 20s linear infinite;

      &::before {
        content: '';
        position: absolute;
        top: 20px;
        left: 20px;
        right: 20px;
        bottom: 20px;
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 50%;
      }
    }

    .tech-ring-2 {
      position: absolute;
      width: 150px;
      height: 150px;
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 50%;
      bottom: 20%;
      right: -30px;
      animation: ring-rotate 15s linear infinite reverse;
    }

    @keyframes ring-rotate {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    // 更多光晕
    .glow-circle-3 {
      position: absolute;
      width: 250px;
      height: 250px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      animation: pulse 6s ease-in-out infinite;
    }

    @keyframes pulse {
      0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
      50% { transform: translate(-50%, -50%) scale(1.3); opacity: 0.8; }
    }
  }

  @keyframes float {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33% { transform: translate(30px, -30px) scale(1.1); }
    66% { transform: translate(-20px, 20px) scale(0.9); }
  }

  @keyframes particle-float {
    0% { transform: translateY(100vh) scale(0); opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { transform: translateY(-100px) scale(1); opacity: 0; }
  }

  .left-content {
    position: relative;
    z-index: 1;
    max-width: 400px;

    .brand-logo {
      width: 56px;
      height: 56px;
      background: rgba(255,255,255,0.15);
      border: 2px solid rgba(255,255,255,0.3);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 32px;
      backdrop-filter: blur(10px);
    }

    h1 {
      font-size: 42px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 16px;
      line-height: 1.2;
      letter-spacing: -0.5px;

      @media (max-width: 768px) {
        font-size: 28px;
      }
    }

    .left-desc {
      font-size: 18px;
      color: rgba(255, 255, 255, 0.85);
      margin-bottom: 40px;
      line-height: 1.6;

      @media (max-width: 768px) {
        font-size: 15px;
        margin-bottom: 24px;
      }
    }

    .feature-list {
      .feature-item {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        color: rgba(255, 255, 255, 0.8);
        font-size: 15px;

        .feature-dot {
          width: 8px;
          height: 8px;
          background: rgba(255,255,255,0.9);
          border-radius: 50%;
          box-shadow: 0 0 8px rgba(255,255,255,0.5);
        }
      }
    }
  }
}

// 右侧区域（与登录页保持一致）
.register-right {
  flex: 1;
  background: var(--card-bg);
  display: flex;
  flex-direction: column;
  padding: 32px 48px;
  overflow-y: auto;

  @media (max-width: 768px) {
    padding: 24px;
  }

  .right-header {
    text-align: right;
    margin-bottom: 48px;
    font-size: 14px;
    color: var(--text-secondary);

    a {
      color: var(--ant-primary-color);
      cursor: pointer;
      margin-left: 8px;

      &:hover {
        text-decoration: underline;
      }
    }

    @media (max-width: 768px) {
      text-align: center;
      margin-bottom: 24px;
    }
  }

  .right-form {
    max-width: 400px;
    margin: auto;
    width: 100%;

    h2 {
      font-size: 24px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 24px;
    }
  }
}

// 暗色模式覆盖（仅保留左侧区域动画所需的覆盖）
:global(body.dark-theme) {
  .register-left {
    .tech-bg {
      .grid-lines {
        background-image:
          linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
      }
    }
  }
}

// 表单样式（与登录页一致，使用CSS变量自动适配明暗主题）
.auth-form {
  :deep(.ant-form-item-label > label) {
    color: var(--text-primary);
    font-weight: 500;
  }

  :deep(.ant-input) {
    background: var(--bg-secondary);
    border-color: var(--border-color);
    color: var(--text-primary);
    border-radius: 6px;

    &:hover,
    &:focus {
      border-color: var(--ant-primary-color);
      background: var(--bg-primary);
    }

    &::placeholder {
      color: var(--text-tertiary);
    }
  }

  :deep(.ant-input-affix-wrapper) {
    background: var(--bg-secondary) !important;
    border-color: var(--border-color) !important;
    border-radius: 6px;

    .ant-input {
      background: transparent !important;
      color: var(--text-primary) !important;
      box-shadow: none !important;

      &::placeholder {
        color: var(--text-tertiary) !important;
      }
    }

    .anticon {
      color: var(--text-tertiary) !important;
    }

    &:hover,
    &:focus {
      border-color: var(--ant-primary-color) !important;
      background: var(--bg-primary) !important;
    }
  }

  :deep(.ant-btn-primary) {
    background: var(--ant-primary-color);
    border-color: var(--ant-primary-color);
    border-radius: 6px;
    height: 44px;
    font-size: 16px;
    font-weight: 500;

    &:hover {
      background: var(--ant-primary-color-hover);
      border-color: var(--ant-primary-color-hover);
    }
  }
}

// 验证码
.captcha-row {
  display: flex;
  gap: 12px;
  align-items: center;

  .captcha-img {
    height: 40px;
    border-radius: 6px;
    cursor: pointer;
    border: 1px solid var(--border-color);
    background: #fff;
    object-fit: contain;
  }
}
</style>
