/**
 * 极简 Markdown → HTML 转换（无第三方依赖）
 *
 * 用途：渲染 AI 返回的 Markdown 文本，避免直接显示 #、**、- 等原始符号。
 *
 * 支持语法：
 *   标题        # / ## / ### ...
 *   加粗        **文本**
 *   斜体        *文本*
 *   无序列表    - 或 * 或 · 或 •
 *   有序列表    1. 或 1、或 1)
 *   引用        > 文本
 *   分隔线      --- 或 ***
 *   行内代码    `code`
 *   代码块      ```...```
 *
 * 额外支持本项目 AI 输出常用的【板块标题】格式（渲染为强调板块条）。
 *
 * 安全：所有内容先做 HTML 转义，再解析 Markdown，避免 XSS。
 */

/** HTML 转义，防止 AI 输出中的标签被当成真实 HTML 执行 */
function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

/** 行内语法解析（输入已转义） */
function renderInline(text) {
  let s = escapeHtml(text)
  // 行内代码（优先处理，避免其中的 * 被当成强调）
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>')
  // 加粗 **x**
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  // 斜体 *x*（前面不能是 *，避免与加粗冲突）
  s = s.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>')
  return s
}

/**
 * 将 Markdown 源文本转为 HTML
 * @param {string} src Markdown 文本
 * @returns {string} HTML 字符串
 */
export function renderMarkdown(src) {
  if (!src) return ''

  const lines = String(src).replace(/\r\n?/g, '\n').split('\n')
  const out = []
  let listType = null // 'ul' | 'ol'
  let inCode = false
  let codeBuf = []
  let para = []

  const closeList = () => {
    if (listType) {
      out.push(`</${listType}>`)
      listType = null
    }
  }
  const flushPara = () => {
    if (para.length) {
      out.push(`<p>${para.map(renderInline).join('<br>')}</p>`)
      para = []
    }
  }

  for (const raw of lines) {
    const line = raw.replace(/\s+$/, '')

    // ---- 代码块 ----
    if (/^\s*```/.test(line)) {
      if (inCode) {
        out.push(`<pre><code>${escapeHtml(codeBuf.join('\n'))}</code></pre>`)
        codeBuf = []
        inCode = false
      } else {
        flushPara()
        closeList()
        inCode = true
      }
      continue
    }
    if (inCode) {
      codeBuf.push(raw)
      continue
    }

    // ---- 空行：结束当前段落/列表 ----
    if (!line.trim()) {
      flushPara()
      closeList()
      continue
    }

    // ---- 标题 # ----
    const heading = line.match(/^(#{1,6})\s+(.*)$/)
    if (heading) {
      flushPara()
      closeList()
      const level = Math.min(heading[1].length, 4) // 最多渲染到 h4，避免过大
      out.push(`<h${level}>${renderInline(heading[2])}</h${level}>`)
      continue
    }

    // ---- 本项目特有：【板块标题】----
    const panel = line.match(/^\s*【(.+)】\s*$/)
    if (panel) {
      flushPara()
      closeList()
      out.push(`<div class="md-panel"><span>${renderInline(panel[1])}</span></div>`)
      continue
    }

    // ---- 分隔线 --- ----
    if (/^\s*(-{3,}|\*{3,})\s*$/.test(line)) {
      flushPara()
      closeList()
      out.push('<hr>')
      continue
    }

    // ---- 引用 > ----
    if (/^\s*>\s?/.test(line)) {
      flushPara()
      closeList()
      out.push(`<blockquote>${renderInline(line.replace(/^\s*>\s?/, ''))}</blockquote>`)
      continue
    }

    // ---- 无序列表 - * · • ----
    const ul = line.match(/^\s*[-*·•]\s+(.*)$/)
    if (ul) {
      flushPara()
      if (listType !== 'ul') {
        closeList()
        out.push('<ul>')
        listType = 'ul'
      }
      out.push(`<li>${renderInline(ul[1])}</li>`)
      continue
    }

    // ---- 有序列表 1. ----
    const ol = line.match(/^\s*\d+[.、)]\s+(.*)$/)
    if (ol) {
      flushPara()
      if (listType !== 'ol') {
        closeList()
        out.push('<ol>')
        listType = 'ol'
      }
      out.push(`<li>${renderInline(ol[1])}</li>`)
      continue
    }

    // ---- 普通段落 ----
    closeList()
    para.push(line)
  }

  // 未闭合的代码块兜底输出
  if (inCode && codeBuf.length) {
    out.push(`<pre><code>${escapeHtml(codeBuf.join('\n'))}</code></pre>`)
  }
  flushPara()
  closeList()

  return out.join('')
}

export default renderMarkdown
