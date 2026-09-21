const api = require('../../utils/api')

Page({
  data: {
    clubs: [],
    filtered: [],
    keyword: '',
    loading: true,
    error: ''
  },

  onLoad() {
    this.load()
  },

  // 从新增 / 编辑 / 详情页返回时刷新一次
  onShow() {
    if (this.hasLoaded) {
      this.load(true)
    }
  },

  // 下拉刷新：强制重新请求
  onPullDownRefresh() {
    this.load(true).then(function () {
      wx.stopPullDownRefresh()
    })
  },

  load(force) {
    const that = this
    this.setData({ loading: true, error: '' })
    return api
      .getClubs(force)
      .then(function (clubs) {
        that.hasLoaded = true
        that.setData({ clubs: clubs, loading: false })
        that.applyFilter()
      })
      .catch(function (err) {
        that.setData({ loading: false, error: err.message || '加载失败' })
      })
  },

  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
    this.applyFilter()
  },

  onClear() {
    this.setData({ keyword: '' })
    this.applyFilter()
  },

  // 纯前端过滤，数据量小，够用
  applyFilter() {
    const kw = this.data.keyword.trim().toLowerCase()
    if (!kw) {
      this.setData({ filtered: this.data.clubs })
      return
    }
    const filtered = this.data.clubs.filter(function (c) {
      return (
        c.name.toLowerCase().indexOf(kw) > -1 ||
        c.category.toLowerCase().indexOf(kw) > -1 ||
        c.description.toLowerCase().indexOf(kw) > -1
      )
    })
    this.setData({ filtered: filtered })
  },

  goDetail(e) {
    wx.navigateTo({
      url: '/pages/detail/detail?id=' + e.currentTarget.dataset.id
    })
  },

  goCreate() {
    wx.navigateTo({ url: '/pages/edit/edit' })
  }
})
