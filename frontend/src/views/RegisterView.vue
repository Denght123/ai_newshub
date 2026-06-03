<template>
  <main class="auth-page">
    <section class="auth-panel">
      <AppLogo />
      <div>
        <h1>创建账号</h1>
        <p>先建立一个轻量后台账号，后续就能和 FastAPI 接口完整联调。</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="handleSubmit">
        <el-form-item label="用户名" prop="username">
          <el-input v-model.trim="form.username" size="large" autocomplete="username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model.trim="form.email" size="large" type="email" autocomplete="email" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" size="large" type="password" show-password autocomplete="new-password" />
        </el-form-item>
        <el-button type="primary" native-type="submit" size="large" :loading="submitting" class="submit-button">
          注册
        </el-button>
      </el-form>

      <p class="switch-text">
        已经有账号？
        <RouterLink class="text-link" to="/login">去登录</RouterLink>
      </p>
    </section>
  </main>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import AppLogo from '@/components/AppLogo.vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: ['blur', 'change'] },
  ],
  password: [{ min: 6, required: true, message: '密码至少 6 位', trigger: 'blur' }],
}

async function handleSubmit() {
  const valid = await formRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    await authStore.register(form)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '注册失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.auth-page {
  position: relative;
  display: grid;
  min-height: 100dvh;
  place-items: center;
  padding: 24px;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(255, 250, 240, 0.82), rgba(239, 225, 201, 0.72)),
    repeating-linear-gradient(
      0deg,
      transparent 0,
      transparent 31px,
      var(--nh-line) 32px,
      transparent 33px
    );
}

.auth-page::before {
  position: absolute;
  inset: 18px;
  z-index: -1;
  content: "";
  border: 1px solid rgba(205, 179, 139, 0.36);
  border-radius: var(--nh-radius);
  pointer-events: none;
}

.auth-panel {
  position: relative;
  display: grid;
  width: min(460px, 100%);
  gap: 24px;
  padding: 36px;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(255, 253, 248, 0.98), rgba(255, 250, 240, 0.92)),
    var(--nh-paper);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
  box-shadow: var(--nh-shadow);
  animation: nh-fade-up 340ms var(--nh-transition) both;
}

.auth-panel::before {
  position: absolute;
  inset: 0;
  pointer-events: none;
  content: "";
  background:
    repeating-linear-gradient(
      0deg,
      transparent 0,
      transparent 31px,
      rgba(145, 108, 62, 0.055) 32px,
      transparent 33px
    );
  opacity: 0.65;
}

.auth-panel > * {
  position: relative;
}

h1 {
  margin: 0;
  font-family: var(--nh-font-heading);
  font-size: 34px;
  font-weight: 750;
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
