export const contentTransform = (content: string) => {
  // 处理空内容或非字符串内容
  if (content && typeof content === 'string' && !content.startsWith('<')) {
    // 检查是否包含 Markdown 标题语法
    const hasMarkdownHeadings =
      /^#{1,6}\s/.test(content) || content.includes('\n#')

    if (hasMarkdownHeadings) {
      // 如果包含 Markdown 标题，直接返回让 Tiptap 处理
      return content
    }

    // 处理纯文本中的换行符
    console.log(content.split('\n'))
    return content
      .split('\n')
      .map((line) => `<p>${line}</p>`)
      .join('')
  }

  return content
}
