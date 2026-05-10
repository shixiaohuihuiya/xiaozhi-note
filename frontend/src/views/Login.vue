<template>
  <div class="login-page">
    <!-- 左侧科技区域 -->
    <div class="login-left">
      <div class="tech-bg">
        <!-- 脉冲波纹 -->
        <div class="ripple-container">
          <span v-for="n in 5" :key="'r' + n" :class="'ripple r' + n"></span>
        </div>
        <!-- 轨道粒子 -->
        <div class="orbit-container">
          <span
            v-for="n in 12"
            :key="'o' + n"
            :class="'orbit-dot o' + n"
            :style="{ '--orbit-radius': (60 + n * 15) + 'px' }"
          ></span>
        </div>
        <!-- 对角光束 -->
        <div class="beam-container">
          <span v-for="n in 6" :key="'b' + n" :class="'beam b' + n"></span>
        </div>
        <!-- 浮动符号 -->
        <div class="float-symbols">
          <span v-for="n in 20" :key="'f' + n" :class="'fsym f' + n">{{ ['0','1','+','-','*','/','=','<','>','{','}','[',']','|','&','%','$','#','@','!'][n-1] }}</span>
        </div>
        <!-- 六边形网格 -->
        <div class="hex-grid">
          <span v-for="n in 40" :key="'h' + n" :class="'hex h' + n"></span>
        </div>
      </div>
      <div class="left-content">
        <div class="brand-logo">XZ</div>
        <h1>欢迎回来</h1>
        <p class="left-desc">登录小智笔记，继续你的智能创作</p>
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

    <!-- 右侧表单区域 -->
    <div class="login-right">
      <div class="right-header">
        <span>还没有账号？</span>
        <a @click="$router.push('/register')">立即注册 →</a>
      </div>

      <div class="right-form">
        <h2>登录小智笔记</h2>

        <a-form
          :model="formState"
          :rules="rules"
          @finish="handleSubmit"
          class="auth-form"
          layout="vertical"
        >
          <a-form-item label="用户名或邮箱" name="account">
            <a-input
              v-model:value="formState.account"
              placeholder="请输入用户名或邮箱"
              size="large"
            >
              <template #prefix><UserOutlined /></template>
            </a-input>
          </a-form-item>

          <a-form-item label="密码" name="password">
            <a-input-password
              v-model:value="formState.password"
              placeholder="请输入密码"
              size="large"
            >
              <template #prefix><LockOutlined /></template>
            </a-input-password>
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
              登录
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
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { useUserStore } from '@/stores/user'
import { getCaptcha } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const captchaImage = ref('')
const captchaKey = ref('')

const formState = reactive({
  account: '',
  password: '',
  captcha_code: ''
})

const rules = {
  account: [{ required: true, message: '请输入用户名或邮箱' }],
  password: [{ required: true, message: '请输入密码' }],
  captcha_code: [{ required: true, message: '请输入验证码' }]
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
    const res = await userStore.login({
      account: formState.account,
      password: formState.password,
      captcha_key: captchaKey.value,
      captcha_code: formState.captcha_code
    })
    if (res.code === 200) {
      if (res.data.must_change_password) {
        message.warning('管理员已重置您的密码，请先修改密码')
        router.push('/user/password?force=1')
      } else {
        message.success('登录成功')
        router.push('/')
      }
    }
  } catch (error) {
    console.error('登录错误:', error)
    message.error(error.message || error.response?.data?.message || '登录失败')
    // 登录失败后刷新验证码
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
.login-page {
  min-height: 100vh;
  display: flex;

  @media (max-width: 768px) {
    flex-direction: column;
  }
}

// 左侧区域
.login-left {
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

    // 脉冲波纹
    .ripple-container {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 0;
      height: 0;

      .ripple {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 50%;
        animation: ripple-expand 4s ease-out infinite;

        &.r1 { width: 100px; height: 100px; animation-delay: 0s; }
        &.r2 { width: 200px; height: 200px; animation-delay: 0.8s; }
        &.r3 { width: 300px; height: 300px; animation-delay: 1.6s; }
        &.r4 { width: 400px; height: 400px; animation-delay: 2.4s; }
        &.r5 { width: 500px; height: 500px; animation-delay: 3.2s; }
      }
    }

    @keyframes ripple-expand {
      0% { transform: translate(-50%, -50%) scale(0.5); opacity: 0.6; }
      100% { transform: translate(-50%, -50%) scale(2); opacity: 0; }
    }

    // 轨道粒子
    .orbit-container {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 0;
      height: 0;

      .orbit-dot {
        position: absolute;
        width: 4px;
        height: 4px;
        background: rgba(255, 255, 255, 0.7);
        border-radius: 50%;
        box-shadow: 0 0 6px rgba(255, 255, 255, 0.5);
        animation: orbit-rotate linear infinite;

        &.o1 { animation-duration: 6s; animation-delay: 0s; }
        &.o2 { animation-duration: 8s; animation-delay: 0.5s; }
        &.o3 { animation-duration: 10s; animation-delay: 1s; }
        &.o4 { animation-duration: 7s; animation-delay: 1.5s; }
        &.o5 { animation-duration: 9s; animation-delay: 2s; }
        &.o6 { animation-duration: 11s; animation-delay: 2.5s; }
        &.o7 { animation-duration: 6.5s; animation-delay: 3s; }
        &.o8 { animation-duration: 8.5s; animation-delay: 3.5s; }
        &.o9 { animation-duration: 10.5s; animation-delay: 4s; }
        &.o10 { animation-duration: 7.5s; animation-delay: 4.5s; }
        &.o11 { animation-duration: 9.5s; animation-delay: 5s; }
        &.o12 { animation-duration: 11.5s; animation-delay: 5.5s; }
      }
    }

    @keyframes orbit-rotate {
      0% { transform: rotate(0deg) translateX(var(--orbit-radius, 100px)) rotate(0deg); }
      100% { transform: rotate(360deg) translateX(var(--orbit-radius, 100px)) rotate(-360deg); }
    }

    // 对角光束
    .beam-container {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      overflow: hidden;

      .beam {
        position: absolute;
        width: 2px;
        height: 200px;
        background: linear-gradient(to bottom, transparent, rgba(255,255,255,0.2), transparent);
        animation: beam-move 5s ease-in-out infinite;

        &.b1 { left: 10%; top: -200px; animation-delay: 0s; transform: rotate(45deg); }
        &.b2 { left: 30%; top: -200px; animation-delay: 1s; transform: rotate(45deg); }
        &.b3 { left: 50%; top: -200px; animation-delay: 2s; transform: rotate(45deg); }
        &.b4 { left: 70%; top: -200px; animation-delay: 3s; transform: rotate(45deg); }
        &.b5 { left: 90%; top: -200px; animation-delay: 4s; transform: rotate(45deg); }
        &.b6 { left: 20%; top: -200px; animation-delay: 2.5s; transform: rotate(45deg); }
      }
    }

    @keyframes beam-move {
      0% { transform: translateY(0) rotate(45deg); opacity: 0; }
      30% { opacity: 1; }
      70% { opacity: 1; }
      100% { transform: translateY(calc(100vh + 400px)) rotate(45deg); opacity: 0; }
    }

    // 浮动符号
    .float-symbols {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      font-family: 'Courier New', monospace;
      font-size: 14px;
      font-weight: 600;
      color: rgba(255, 255, 255, 0.12);
      overflow: hidden;
      pointer-events: none;

      .fsym {
        position: absolute;
        animation: float-up 10s linear infinite;

        &.f1 { left: 5%; top: 100%; animation-delay: 0s; }
        &.f2 { left: 12%; top: 100%; animation-delay: 0.5s; }
        &.f3 { left: 18%; top: 100%; animation-delay: 1s; }
        &.f4 { left: 25%; top: 100%; animation-delay: 1.5s; }
        &.f5 { left: 32%; top: 100%; animation-delay: 2s; }
        &.f6 { left: 38%; top: 100%; animation-delay: 2.5s; }
        &.f7 { left: 45%; top: 100%; animation-delay: 3s; }
        &.f8 { left: 52%; top: 100%; animation-delay: 3.5s; }
        &.f9 { left: 58%; top: 100%; animation-delay: 4s; }
        &.f10 { left: 65%; top: 100%; animation-delay: 4.5s; }
        &.f11 { left: 72%; top: 100%; animation-delay: 5s; }
        &.f12 { left: 78%; top: 100%; animation-delay: 5.5s; }
        &.f13 { left: 85%; top: 100%; animation-delay: 6s; }
        &.f14 { left: 92%; top: 100%; animation-delay: 6.5s; }
        &.f15 { left: 8%; top: 100%; animation-delay: 7s; }
        &.f16 { left: 15%; top: 100%; animation-delay: 7.5s; }
        &.f17 { left: 22%; top: 100%; animation-delay: 8s; }
        &.f18 { left: 35%; top: 100%; animation-delay: 8.5s; }
        &.f19 { left: 48%; top: 100%; animation-delay: 9s; }
        &.f20 { left: 68%; top: 100%; animation-delay: 9.5s; }
      }
    }

    @keyframes float-up {
      0% { transform: translateY(0) rotate(0deg); opacity: 0; }
      10% { opacity: 0.8; }
      90% { opacity: 0.8; }
      100% { transform: translateY(-120vh) rotate(360deg); opacity: 0; }
    }

    // 六边形网格
    .hex-grid {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;

      .hex {
        position: absolute;
        width: 6px;
        height: 6px;
        background: rgba(255, 255, 255, 0.15);
        border-radius: 50%;
        animation: hex-pulse 3s ease-in-out infinite;

        &.h1 { top: 10%; left: 10%; animation-delay: 0s; }
        &.h2 { top: 10%; left: 30%; animation-delay: 0.2s; }
        &.h3 { top: 10%; left: 50%; animation-delay: 0.4s; }
        &.h4 { top: 10%; left: 70%; animation-delay: 0.6s; }
        &.h5 { top: 10%; left: 90%; animation-delay: 0.8s; }
        &.h6 { top: 25%; left: 20%; animation-delay: 1s; }
        &.h7 { top: 25%; left: 40%; animation-delay: 1.2s; }
        &.h8 { top: 25%; left: 60%; animation-delay: 1.4s; }
        &.h9 { top: 25%; left: 80%; animation-delay: 1.6s; }
        &.h10 { top: 40%; left: 10%; animation-delay: 1.8s; }
        &.h11 { top: 40%; left: 30%; animation-delay: 2s; }
        &.h12 { top: 40%; left: 50%; animation-delay: 2.2s; }
        &.h13 { top: 40%; left: 70%; animation-delay: 2.4s; }
        &.h14 { top: 40%; left: 90%; animation-delay: 2.6s; }
        &.h15 { top: 55%; left: 20%; animation-delay: 0.5s; }
        &.h16 { top: 55%; left: 40%; animation-delay: 0.7s; }
        &.h17 { top: 55%; left: 60%; animation-delay: 0.9s; }
        &.h18 { top: 55%; left: 80%; animation-delay: 1.1s; }
        &.h19 { top: 70%; left: 10%; animation-delay: 1.3s; }
        &.h20 { top: 70%; left: 30%; animation-delay: 1.5s; }
        &.h21 { top: 70%; left: 50%; animation-delay: 1.7s; }
        &.h22 { top: 70%; left: 70%; animation-delay: 1.9s; }
        &.h23 { top: 70%; left: 90%; animation-delay: 2.1s; }
        &.h24 { top: 85%; left: 20%; animation-delay: 2.3s; }
        &.h25 { top: 85%; left: 40%; animation-delay: 2.5s; }
        &.h26 { top: 85%; left: 60%; animation-delay: 2.7s; }
        &.h27 { top: 85%; left: 80%; animation-delay: 0.3s; }
        &.h28 { top: 15%; left: 15%; animation-delay: 0.6s; }
        &.h29 { top: 15%; left: 55%; animation-delay: 0.9s; }
        &.h30 { top: 15%; left: 85%; animation-delay: 1.2s; }
        &.h31 { top: 50%; left: 5%; animation-delay: 1.5s; }
        &.h32 { top: 50%; left: 45%; animation-delay: 1.8s; }
        &.h33 { top: 50%; left: 75%; animation-delay: 2.1s; }
        &.h34 { top: 65%; left: 25%; animation-delay: 0.4s; }
        &.h35 { top: 65%; left: 55%; animation-delay: 0.7s; }
        &.h36 { top: 65%; left: 95%; animation-delay: 1s; }
        &.h37 { top: 80%; left: 5%; animation-delay: 1.3s; }
        &.h38 { top: 80%; left: 35%; animation-delay: 1.6s; }
        &.h39 { top: 80%; left: 65%; animation-delay: 1.9s; }
        &.h40 { top: 80%; left: 95%; animation-delay: 2.2s; }
      }
    }

    @keyframes hex-pulse {
      0%, 100% { transform: scale(1); opacity: 0.2; }
      50% { transform: scale(1.8); opacity: 0.6; }
    }
  }

  .left-content {
    position: relative;
    z-index: 1;
    max-width: 400px;

    .brand-logo {
      width: 56px;
      height: 56px;
      background: rgba(255, 255, 255, 0.15);
      border: 2px solid rgba(255, 255, 255, 0.3);
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
          background: rgba(255, 255, 255, 0.9);
          border-radius: 50%;
          box-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
        }
      }
    }
  }
}

// 右侧区域
.login-right {
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

// 表单样式
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
