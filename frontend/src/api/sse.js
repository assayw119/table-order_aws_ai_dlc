// SSE 구독 React 훅: 자동 연결/해제 + 지수 백오프 재연결 (US-T1, FE-NFR-R1)
import { useEffect, useRef } from 'react'
import { API_BASE } from './config.js'

const EVENT_TYPES = [
  'order_created',
  'order_status_changed',
  'order_deleted',
  'session_closed',
]

/**
 * @param {string|null} path - SSE 엔드포인트 경로 (null이면 비활성)
 * @param {string|null} token - 인증 토큰 (쿼리로 전달)
 * @param {(event:object)=>void} onEvent - 이벤트 콜백
 */
export function useSse(path, token, onEvent) {
  const onEventRef = useRef(onEvent)
  onEventRef.current = onEvent

  useEffect(() => {
    if (!path || !token) return
    let es = null
    let retry = 0
    let closed = false
    let timer = null

    const connect = () => {
      if (closed) return
      const url = `${API_BASE}${path}?token=${encodeURIComponent(token)}`
      es = new EventSource(url)

      const handler = (e) => {
        try {
          const data = JSON.parse(e.data)
          onEventRef.current && onEventRef.current(data)
        } catch {
          // ping 등 비-JSON 무시
        }
      }
      EVENT_TYPES.forEach((t) => es.addEventListener(t, handler))
      es.onmessage = handler

      es.onopen = () => {
        retry = 0
      }
      es.onerror = () => {
        es && es.close()
        if (closed) return
        // 지수 백오프 (상한 30초)
        const delay = Math.min(1000 * 2 ** retry, 30000)
        retry += 1
        timer = setTimeout(connect, delay)
      }
    }

    connect()

    return () => {
      closed = true
      if (timer) clearTimeout(timer)
      if (es) es.close()
    }
  }, [path, token])
}
