import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({ html: false, linkify: true, breaks: true })

export const contentTransform = (content: string) => {
  if (content && typeof content === 'string' && !content.startsWith('<')) {
    // 判斷是否像 Markdown（標題/列表/粗斜體/連結等）
    const looksLikeMarkdown =
      /^#{1,6}\s/.test(content) || // 標題
      /(^|\n)(-|\*|\+)\s+/.test(content) || // 無序列表
      /(^|\n)\d+\.\s+/.test(content) || // 有序列表
      /\*\*.+\*\*|__.+__|\*.+\*|_.+_/.test(content) || // 粗斜體
      /\[.+\]\(.+\)/.test(content) // 連結

    if (looksLikeMarkdown) {
      // 轉為 HTML 交由編輯器解析
      return md.render(content)
    }

    // 純文字：以換行分段
    return content
      .split('\n')
      .map((line) => `<p>${line}</p>`)
      .join('')
  }

  return content
}
