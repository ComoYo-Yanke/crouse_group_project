import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getProfile } from '@/api/user'

/**
 * 用户状态管理
 */
export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userId = ref(Number(localStorage.getItem('userId')) || null)
  const profile = ref(null)

  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => profile.value?.username || '')

  function setLogin({ token: t, userId: id }) {
    token.value = t
    userId.value = id
    localStorage.setItem('token', t)
    localStorage.setItem('userId', id)
  }

  function logout() {
    token.value = ''
    userId.value = null
    profile.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userId')
  }

  async function fetchProfile() {
    profile.value = await getProfile()
    return profile.value
  }

  return { token, userId, profile, isLoggedIn, username, setLogin, logout, fetchProfile }
})
