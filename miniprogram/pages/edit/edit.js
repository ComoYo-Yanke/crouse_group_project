const api = require('../../utils/api')

Page({
  data: {
    id: 0,
    isEdit: false,
    loading: false,
    saving: false,
    error: '',
    today: '',
    form: { name: '', category: '', foundedDate: '', location: '', description: '' }
  },

  onLoad(options) {
    // 带 id 就是编辑，不带就是新增
    const isEdit = !!options.id
    if (isEdit) {
      this.setData({ id: Number(options.id), isEdit: true })
      wx.setNavigationBarTitle({ title: '编辑社团' })
      this.load()
    } else {
      wx.setNavigationBarTitle({ title: '新增社团' })
    }
  },

  load() {
    const that = this
    this.setData({ loading: true, error: '' })
    api
      .getClubById(this.data.id)
      .then(function (club) {
        that.setData({
          loading: false,
          form: {
            name: club.name,
            category: club.category,
            foundedDate: club.foundedDate,
            // 列表里的兜底文案不要带进表单
            location: club.location === '待定' ? '' : club.location,
            description: club.description === '暂无简介' ? '' : club.description
          }
        })
      })
      .catch(function (err) {
        that.setData({ loading: false, error: err.message || '加载失败' })
      })
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field
    const patch = {}
    patch['form.' + field] = e.detail.value
    this.setData(patch)
  },

  onDateChange(e) {
    this.setData({ 'form.foundedDate': e.detail.value })
  },

  onSubmit() {
    if (this.data.saving) return

    const form = this.data.form
    const checks = [
      ['name', '请填写社团名称'],
      ['category', '请填写社团类型'],
      ['foundedDate', '请选择成立日期'],
      ['description', '请填写社团简介']
    ]
    for (let i = 0; i < checks.length; i++) {
      if (!String(form[checks[i][0]] || '').trim()) {
        wx.showToast({ title: checks[i][1], icon: 'none' })
        return
      }
    }

    const payload = {
      name: form.name.trim(),
      category: form.category.trim(),
      foundedDate: form.foundedDate,
      location: form.location.trim(),
      description: form.description.trim()
    }

    const that = this
    this.setData({ saving: true })
    const task = this.data.isEdit
      ? api.updateClub(this.data.id, payload)
      : api.createClub(payload)

    task
      .then(function () {
        wx.showToast({ title: that.data.isEdit ? '已保存' : '已创建', icon: 'success' })
        // 等提示显示完再返回，上一页 onShow 会自动刷新
        setTimeout(function () {
          wx.navigateBack()
        }, 700)
      })
      .catch(function (err) {
        that.setData({ saving: false })
        wx.showModal({ title: '保存失败', content: err.message, showCancel: false })
      })
  }
})
