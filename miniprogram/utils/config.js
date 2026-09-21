/**
 * 小程序请求配置。
 *
 * baseUrl：Django 开发服务器地址。
 *   - 真机预览时改成电脑的局域网 IP，例如 http://192.168.1.10:8000
 *   - 开发者工具里勾选「详情 → 本地设置 → 不校验合法域名」
 *
 * useMock：后端没启动时改成 true，直接用 utils/mock.js 里的假数据看界面。
 */
module.exports = {
  baseUrl: 'http://127.0.0.1:8000',
  useMock: false,
  timeout: 8000
}
