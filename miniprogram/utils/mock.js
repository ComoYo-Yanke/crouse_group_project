/**
 * 离线假数据，字段与 GET /api/clubs/ 的返回保持一致。
 * 在 utils/config.js 里把 useMock 改成 true 即可启用。
 */
const response = {
  count: 2,
  results: [
    {
      id: 1,
      name: '篮球社',
      description: '每周三、周六下午在体育馆训练，欢迎零基础同学加入。',
      category: '体育',
      founded_date: '2019-09-01',
      location: '体育馆 3 号场',
      administrators: [
        {
          id: 1,
          real_name: '张伟',
          username: '社团管理员1',
          is_staff: true,
          phone: '13800000001',
          email: 'zhangwei@example.com'
        }
      ]
    },
    {
      id: 2,
      name: '摄影社',
      description: '组织外拍、暗房体验和作品评图，设备社内可借用。',
      category: '文艺',
      founded_date: '2020-03-15',
      location: '艺术楼 204',
      administrators: [
        {
          id: 2,
          real_name: '李娜',
          username: '社团管理员2',
          is_staff: true,
          phone: '13800000002',
          email: 'lina@example.com'
        }
      ]
    }
  ]
}

module.exports = { response }
