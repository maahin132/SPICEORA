import { useCallback, useEffect, useMemo, useState } from 'react'
import { authRequest } from '../api/auth.js'
import { AuthContext } from './context.js'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [ready, setReady] = useState(false)
  const [sessionError, setSessionError] = useState('')

  const refresh = useCallback(async () => {
    try {
      const result = await authRequest('auth/me/')
      setUser(result.user)
      setSessionError('')
    } catch (error) {
      setUser(null)
      setSessionError(error.status === 401 ? '' : error.message)
    } finally {
      setReady(true)
    }
  }, [])

  useEffect(() => {
    Promise.resolve().then(refresh)
  }, [refresh])

  const signIn = useCallback(async (identity, password, audience) => {
    const endpoint =
      audience === 'staff' ? 'auth/operations/login/' : 'auth/login/'
    const result = await authRequest(endpoint, {
      method: 'POST',
      body: { identity, password },
    })
    setUser(result.user)
    setSessionError('')
    return result.user
  }, [])

  const signOut = useCallback(async () => {
    await authRequest('auth/logout/', { method: 'POST', body: {} })
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, ready, sessionError, signIn, signOut, refresh }),
    [user, ready, sessionError, signIn, signOut, refresh],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
