import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { title: '注册', public: true }
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'home',
        component: () => import('@/views/HomeView.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'record/create',
        name: 'record-create',
        component: () => import('@/views/record/RecordCreateView.vue'),
        meta: { title: '记录一餐' }
      },
      {
        path: 'record/list',
        name: 'record-list',
        component: () => import('@/views/record/RecordListView.vue'),
        meta: { title: '我的记录' }
      },
      {
        path: 'report',
        name: 'report',
        component: () => import('@/views/report/ReportView.vue'),
        meta: { title: '营养报告' }
      },
      {
        path: 'advice',
        name: 'advice',
        component: () => import('@/views/ai/AdviceView.vue'),
        meta: { title: 'AI 营养师建议' }
      },
      {
        path: 'recipe',
        name: 'recipe',
        component: () => import('@/views/ai/RecipeView.vue'),
        meta: { title: 'AI 菜谱生成' }
      },
      {
        path: 'square',
        name: 'square',
        component: () => import('@/views/square/SquareView.vue'),
        meta: { title: '健康广场' }
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('@/views/user/ProfileView.vue'),
        meta: { title: '个人画像' }
      },
      {
        path: 'user/:userId',
        name: 'user-home',
        component: () => import('@/views/user/UserHomeView.vue'),
        meta: { title: '个人主页' }
      }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/home' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫：未登录跳转登录页
router.beforeEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} - 私人营养师` : '私人营养师'
  const userStore = useUserStore()
  if (!to.meta.public && !userStore.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})

export default router
