<template>
  <pre class="code-block"><code ref="codeRef" :class="languageClass">{{ code }}</code></pre>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import hljs from 'highlight.js/lib/core'
import json from 'highlight.js/lib/languages/json'
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
import xml from 'highlight.js/lib/languages/xml'

hljs.registerLanguage('json', json)
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('xml', xml)

const props = withDefaults(
  defineProps<{
    code?: string
    language?: string
  }>(),
  {
    code: '',
    language: 'json',
  },
)

const codeRef = ref<HTMLElement>()
const languageClass = computed(() => `language-${props.language}`)

async function highlight() {
  await nextTick()
  if (codeRef.value) {
    codeRef.value.removeAttribute('data-highlighted')
    hljs.highlightElement(codeRef.value)
  }
}

onMounted(highlight)
watch(() => props.code, highlight)
</script>

<style scoped>
.code-block {
  margin: 0;
  padding: 16px;
  overflow: auto;
  background: #f1f6f2;
  border: 1px solid #dce6df;
  border-radius: 8px;
  line-height: 1.7;
}
</style>
