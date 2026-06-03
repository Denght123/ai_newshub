<template>
  <div class="app-logo">
    <div class="mark" aria-hidden="true">
      <span />
    </div>
    <div>
      <strong>AI NewsHub</strong>
      <small>每日资讯 RAG 知识库</small>
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
  border: 1px solid var(--nh-border-strong);
  border-radius: var(--nh-radius);
  background:
    linear-gradient(135deg, var(--nh-paper-soft), var(--nh-soft)),
    var(--nh-paper);
  box-shadow: 0 12px 24px rgba(84, 60, 28, 0.14);
}

.mark::before {
  position: absolute;
  top: 0;
  right: 0;
  width: 13px;
  height: 13px;
  content: "";
  background: linear-gradient(135deg, rgba(232, 240, 235, 0.9), rgba(205, 179, 139, 0.72));
  border-bottom: 1px solid var(--nh-border-strong);
  border-left: 1px solid var(--nh-border-strong);
  border-radius: 0 0 0 6px;
}

.mark span {
  position: relative;
  width: 16px;
  height: 16px;
  border: 2px solid var(--nh-primary);
  border-radius: 50%;
  border-right-color: rgba(53, 97, 90, 0.3);
}

.mark span::after {
  position: absolute;
  right: -7px;
  bottom: -4px;
  width: 8px;
  height: 2px;
  content: "";
  background: var(--nh-primary);
  border-radius: 999px;
  transform: rotate(45deg);
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

</style>
