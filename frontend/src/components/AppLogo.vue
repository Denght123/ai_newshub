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
  min-width: 0;
}

.mark {
  position: relative;
  display: grid;
  flex: 0 0 auto;
  width: 40px;
  height: 40px;
  place-items: center;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.62);
  border-radius: var(--nh-radius);
  background: linear-gradient(145deg, var(--nh-primary), var(--nh-accent));
  box-shadow: 0 12px 28px rgba(45, 108, 223, 0.22);
}

.mark::before {
  position: absolute;
  inset: 4px;
  content: "";
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
}

.mark span {
  position: relative;
  width: 17px;
  height: 17px;
  border: 3px solid rgba(255, 255, 255, 0.94);
  border-radius: 50%;
  border-right-color: rgba(255, 255, 255, 0.45);
  animation: logo-pulse 3.8s ease-in-out infinite;
}

strong,
small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

strong {
  font-size: 18px;
  letter-spacing: 0;
  line-height: 1.16;
  background: linear-gradient(90deg, var(--nh-ink), var(--nh-primary-dark));
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

small {
  margin-top: 4px;
  color: var(--nh-muted);
  font-size: 12px;
  line-height: 1.2;
}

@keyframes logo-pulse {
  0%,
  100% {
    transform: rotate(0deg) scale(1);
  }

  50% {
    transform: rotate(26deg) scale(0.94);
  }
}
</style>
