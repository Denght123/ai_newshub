<template>
  <main class="auth-page">
    <section class="auth-panel">
      <AppLogo />
      <div>
        <h1>欢迎回来</h1>
        <p>继续整理 AI 资讯，把今天的灵感放进一个清楚的位置。</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="handleSubmit">
        <el-form-item label="用户名或邮箱" prop="username_or_email">
          <el-input v-model.trim="form.username_or_email" size="large" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" size="large" type="password" show-password autocomplete="current-password" />
        </el-form-item>
        <el-button type="primary" native-type="submit" size="large" :loading="submitting" class="submit-button">
          登录
        </el-button>
        <el-button size="large" class="submit-button demo-button" :loading="demoLoading" @click="handleDemoLogin">
          查看演示效果
        </el-button>
      </el-form>

      <p class="switch-text">
        还没有账号？
        <RouterLink class="text-link" to="/register">去注册</RouterLink>
      </p>
    </section>
  </main>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import AppLogo from '@/components/AppLogo.vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const submitting = ref(false)
const demoLoading = ref(false)

const form = reactive({
  username_or_email: '',
  password: '',
})

const rules: FormRules = {
  username_or_email: [{ required: true, message: '请输入用户名或邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleSubmit() {
  const valid = await formRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    await authStore.login(form)
    ElMessage.success('登录成功')
    router.push(String(route.query.redirect || '/dashboard'))
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '登录失败，请检查账号密码')
  } finally {
    submitting.value = false
  }
}

async function handleDemoLogin() {
  demoLoading.value = true
  try {
    localStorage.setItem('ai_newshub_mock', '1')
    await authStore.login({
      username_or_email: 'demo',
      password: '123456',
    })
    ElMessage.success('已进入演示模式')
    router.push('/dashboard')
  } finally {
    demoLoading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  position: relative;
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 24px;
  overflow: hidden;
}

.auth-page::before {
  position: absolute;
  inset: 0;
  z-index: -1;
  content: "";
  background:
    linear-gradient(120deg, rgba(45, 108, 223, 0.12), transparent 42%),
    linear-gradient(300deg, rgba(22, 163, 148, 0.13), transparent 48%);
}

.auth-panel {
  display: grid;
  width: min(440px, 100%);
  gap: 24px;
  padding: 36px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
  box-shadow: var(--nh-shadow);
  backdrop-filter: blur(18px);
  animation: nh-fade-up 360ms ease both;
}

h1 {
  margin: 0;
  font-size: 34px;
  letter-spacing: 0;
  line-height: 1.12;
}

p {
  margin: 8px 0 0;
  color: var(--nh-muted);
  line-height: 1.7;
}

.submit-button {
  width: 100%;
}

.demo-button {
  margin: 10px 0 0;
  background: rgba(255, 255, 255, 0.68);
}

.switch-text {
  margin: 0;
  text-align: center;
}

@media (max-width: 520px) {
  .auth-panel {
    padding: 28px;
  }
}
</style>
