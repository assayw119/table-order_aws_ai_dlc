// REST 호출 래퍼: 토큰 첨부, JSON 처리, 에러 정규화
import { API_BASE } from './config.js'

export class ApiError extends Error {
  constructor(status, detail) {
    super(detail || `요청 실패 (${status})`)
    this.status = status
    this.detail = detail
  }
}

async function request(method, path, { body, token } = {}) {
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers['Authorization'] = `Bearer ${token}`

  const resp = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (resp.status === 204) return null

  let data = null
  const text = await resp.text()
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = text
    }
  }

  if (!resp.ok) {
    const detail = data && data.detail ? data.detail : `요청 실패 (${resp.status})`
    throw new ApiError(resp.status, typeof detail === 'string' ? detail : JSON.stringify(detail))
  }
  return data
}

export const api = {
  get: (path, token) => request('GET', path, { token }),
  post: (path, body, token) => request('POST', path, { body, token }),
  put: (path, body, token) => request('PUT', path, { body, token }),
  patch: (path, body, token) => request('PATCH', path, { body, token }),
  del: (path, token) => request('DELETE', path, { token }),
}
