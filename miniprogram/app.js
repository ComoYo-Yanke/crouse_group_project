App({
  globalData: {
    // 列表页加载过的社团，详情页优先从这里取，避免重复请求
    clubs: []
  },

  onLaunch() {
    console.log('社团小程序启动')
  }
})
