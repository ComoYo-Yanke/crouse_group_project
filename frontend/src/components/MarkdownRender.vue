<script setup>
/**
 * Markdown 渲染组件
 * 用法：<MarkdownRender :content="aiText" />
 */
import { computed } from 'vue'
import { renderMarkdown } from '@/utils/markdown'

const props = defineProps({
  content: { type: String, default: '' }
})

// 内容已由 renderMarkdown 做过 HTML 转义，可安全用于 v-html
const html = computed(() => renderMarkdown(props.content))
</script>

<template>
  <div class="markdown-body" v-html="html"></div>
</template>

<style scoped>
/*
 * v-html 生成的元素不会带上 scoped 的 data-v 属性，
 * 因此这里所有子选择器都必须用 :deep()，否则样式不生效。
 */
.markdown-body {
  font-size: 14px;
  line-height: 1.85;
  color: #303133;
  word-break: break-word;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  margin: 18px 0 10px;
  font-weight: 600;
  color: #2c3e50;
  line-height: 1.4;
}

.markdown-body :deep(h1) { font-size: 20px; }
.markdown-body :deep(h2) { font-size: 18px; }
.markdown-body :deep(h3) { font-size: 16px; }
.markdown-body :deep(h4) { font-size: 15px; }

.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  padding-left: 10px;
  border-left: 4px solid #67c23a;
}

.markdown-body :deep(p) {
  margin: 8px 0;
}

/* 【板块标题】渲染成的强调条 */
.markdown-body :deep(.md-panel) {
  margin: 16px 0 8px;
}

.markdown-body :deep(.md-panel span) {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  background: linear-gradient(90deg, #67c23a 0%, #85ce61 100%);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 8px 0;
  padding-left: 22px;
}

.markdown-body :deep(li) {
  margin: 4px 0;
  color: #4e5969;
}

.markdown-body :deep(strong) {
  font-weight: 700;
  color: #2c3e50;
}

.markdown-body :deep(em) {
  font-style: italic;
  color: #606266;
}

.markdown-body :deep(blockquote) {
  margin: 10px 0;
  padding: 8px 14px;
  border-left: 4px solid #dcdfe6;
  background: #fafafa;
  border-radius: 0 6px 6px 0;
  color: #606266;
}

.markdown-body :deep(hr) {
  margin: 16px 0;
  border: none;
  border-top: 1px solid #ebeef5;
}

.markdown-body :deep(code) {
  padding: 2px 6px;
  background: #f5f7fa;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 13px;
  color: #e96900;
}

.markdown-body :deep(pre) {
  margin: 10px 0;
  padding: 12px 14px;
  background: #f5f7fa;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  overflow-x: auto;
}

.markdown-body :deep(pre code) {
  padding: 0;
  background: none;
  border: none;
  color: #303133;
}
</style>
