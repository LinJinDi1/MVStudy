type Finding = { severity: string; line_start: number; title: string; description: string; suggestion: string }
export type Review = { summary: string; findings: Finding[] }

export async function reviewSource(source: string): Promise<Review> {
  const response = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/reviews`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source, language: 'python' }),
  })
  const data = await response.json()
  if (!response.ok) throw new Error(data.error?.message || '评审请求失败')
  return data
}
