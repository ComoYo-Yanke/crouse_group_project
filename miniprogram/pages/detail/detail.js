const api = require('../../utils/api')

Page({
  data: {
    id: 0,
    club: null,
    loading: true,
    error: ''
  },

  onLoad(options) {
    this.setData({ id: Number(options.id) })
    this.load()
  },

  // 从编辑页返回时刷新
  onShow() {
    if (this.hasLoaded) {
      this.load()
    }
  },

  load() {
    const that = this
    this.setData({ loading: true, error: '' })
    return api
      .getClubById(this.data.id)
      .then(function (club) {
        that.hasLoaded = true
        that.setData({ club: club, loading: false })
        wx.setNavigationBarTitle({ title: club.name })
      })
      .catch(function (err) {
        that.setData({ loading: false, error: err.message || '加载失败' })
      })
  },

  onCall(e) {
    wx.makePhoneCall({
      phoneNumber: String(e.currentTarget.dataset.phone)
    })
  },

  onCopy(e) {
    wx.setClipboardData({
      data: String(e.currentTarget.dataset.text)
    })
  },

  goEdit() {
    wx.navigateTo({ url: '/pages/edit/edit?id=' + this.data.id })
  },

  onDelete() {
    const that = this
    wx.showModal({
      title: '删除社团',
      content: '确定删除「' + this.data.club.name + '」吗？删除后不可恢复。',
      confirmText: '删除',
      confirmColor: '#e54545',
      success(res) {
        if (!res.confirm) return
        wx.showLoading({ title: '删除中', mask: true })
        api
          .deleteClub(that.data.id)
          .then(function () {
            wx.hideLoading()
            wx.showToast({ title: '已删除', icon: 'success' })
            setTimeout(function () {
              wx.navigateBack()
            }, 700)
          })
          .catch(function (err) {
            wx.hideLoading()
            wx.showModal({ title: '删除失败', content: err.message, showCancel: false })
          })
      }
    })
  }
})
