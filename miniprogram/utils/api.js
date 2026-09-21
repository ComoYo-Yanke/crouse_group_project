const config = require('./config')
const mock = require('./mock')

// 已经拿到的社团列表，详情页复用，避免每次进详情都重新请求。
// 任何增删改之后都会清掉，下次读取自动重新拉。
let cache = null

function errorMessage(res) {
  const data = res.data
  if (data && data.detail) {
    // 表单校验失败时，把第一条具体错误也带出来
    if (data.errors) {
      const first = Object.keys(data.errors)[0]
      if (first) return data.errors[first][0]
    }
    return data.detail
  }
  return '服务器返回 ' + res.statusCode
}

function request(path, method, data) {
  return new Promise(function (resolve, reject) {
    wx.request({
      url: config.baseUrl + path,
      method: method || 'GET',
      data: data,
      header: { 'content-type': 'application/json' },
      timeout: config.timeout,
      success: function (res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject(new Error(errorMessage(res)))
        }
      },
      fail: function () {
        reject(new Error('连不上服务器，请确认 Django 已启动'))
      }
    })
  })
}

function guardMock() {
  if (config.useMock) {
    return Promise.reject(new Error('演示模式（useMock）下不能增删改，请关掉后重试'))
  }
  return null
}

// 后端字段 -> 页面用的字段
function normalize(club) {
  const name = club.name || '未命名社团'
  return {
    id: club.id,
    name: name,
    initial: name.trim().charAt(0),
    description: club.description || '暂无简介',
    category: club.category || '其他',
    location: club.location || '待定',
    foundedDate: club.founded_date || '',
    admins: (club.administrators || []).map(function (a) {
      return {
        id: a.id,
        realName: a.real_name || '未填写',
        phone: a.phone || '',
        email: a.email || ''
      }
    })
  }
}

// 页面字段 -> 后端字段
function toPayload(form) {
  return {
    name: form.name,
    category: form.category,
    founded_date: form.foundedDate,
    location: form.location,
    description: form.description
  }
}

function getClubs(force) {
  if (cache && !force) {
    return Promise.resolve(cache)
  }
  const source = config.useMock ? Promise.resolve(mock.response) : request('/api/clubs/')
  return source.then(function (data) {
    cache = (data.results || []).map(normalize)
    return cache
  })
}

/**
 * 有单条接口了，直接请求；失败再退回列表里找。
 */
function getClubById(id) {
  if (!config.useMock) {
    return request('/api/clubs/' + id + '/').then(normalize)
  }
  return getClubs().then(function (clubs) {
    const found = clubs.filter(function (c) {
      return c.id === id
    })[0]
    if (!found) {
      throw new Error('没有找到这个社团')
    }
    return found
  })
}

function createClub(form) {
  return guardMock() || request('/api/clubs/', 'POST', toPayload(form)).then(function (raw) {
    cache = null
    return normalize(raw)
  })
}

function updateClub(id, form) {
  return (
    guardMock() ||
    request('/api/clubs/' + id + '/', 'PUT', toPayload(form)).then(function (raw) {
      cache = null
      return normalize(raw)
    })
  )
}

function deleteClub(id) {
  return (
    guardMock() ||
    request('/api/clubs/' + id + '/', 'DELETE').then(function (res) {
      cache = null
      return res
    })
  )
}

module.exports = {
  getClubs: getClubs,
  getClubById: getClubById,
  createClub: createClub,
  updateClub: updateClub,
  deleteClub: deleteClub,
  clearCache: function () {
    cache = null
  }
}
