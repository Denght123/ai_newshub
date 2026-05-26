<template>
  <div class="app-logo">
    <div class="mark" aria-hidden="true">
      <span />
    </div>
    <div>
      <strong>AI NewsHub</strong>
      <small>资讯与选题工作台</small>
    </div>
  </div>
</template>

<style scoped>
.app-logo {
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.mark {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 8px;
  background: linear-gradient(145deg, #3d8d7a, #93c7a6);
  box-shadow: 0 10px 28px rgba(61, 141, 122, 0.28);
}

.mark span {
  width: 18px;
  height: 18px;
  border: 3px solid #fff;
  border-radius: 50%;
  border-right-color: rgba(255, 255, 255, 0.45);
}

strong,
small {
  display: block;
}

strong {
  font-size: 18px;
  letter-spacing: 0;
}

small {
  margin-top: 2px;
  color: #718078;
}
</style>
