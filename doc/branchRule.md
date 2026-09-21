# 分支规则

## 长期分支

| 分支 | 用途 | 说明 |
|------|------|------|
| `main` | 主分支 | 始终可运行、可发布，禁止直接提交 |

> 小项目不建 `develop`。有明确发版周期时再考虑。

---

## 临时分支

从 `main` 切出，用完即删。

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feature/` | 新功能 | `feature/heatmap` |
| `fix/` | 修 Bug | `fix/sheet-footer` |
| `hotfix/` | 线上紧急修复 | `hotfix/quota-crash` |
| `refactor/` | 重构 | `refactor/storage-layer` |
| `perf/` | 性能优化 | `perf/chart-dpr` |
| `docs/` | 文档 | `docs/readme-en` |
| `test/` | 测试 | `test/charts-regression` |
| `style/` | 格式 | `style/wxss-tokens` |
| `chore/` | 依赖 / 脚本 / CI | `chore/bump-ucharts` |
| `experiment/` | 实验，一般不合并 | `experiment/canvas-2d` |

---

## 命名规则

```
<类型>/<简短描述>
```

- 全小写
- 单词用 `-` 连接
- 不用中文、空格、下划线
- 描述控制在 3～5 个单词

```
✅ feature/habit-editor
✅ fix/checkin-lock
❌ Feature_HabitEditor
❌ 新功能/打卡弹层
```

---

## 工作流

```
main ──●──────────────●──→  始终可发布
        \            /
         ●──●──●──●        feature 分支，合并后删除
```

```bash
git checkout main && git pull
git checkout -b feature/xxx
# 开发 + 提交
git fetch origin && git rebase origin/main
git push -u origin feature/xxx
# 提 PR → 合并 → 删分支
```

---

## 规则

1. **`main` 禁止直接提交**，一律走 PR
2. **一个分支只做一件事**，不混合功能、修复、重构
3. **分支存活 1～3 天**，超过一周拆分或定期 rebase
4. **合并前必须 rebase `origin/main`**
5. **合并后立即删除**本地和远程分支
6. **`main` 始终可运行**，任何时刻都能编译、能跑

---

## 合并方式

| 方式 | 适用 |
|------|------|
| **Squash and merge** | 小功能，推荐（一个功能 = 一个 commit） |
| **Rebase and merge** | 每个 commit 都有意义时 |
| **Merge commit** | 需要保留完整分叉历史时 |

---

## Commit 规范

```
<type>(<scope>): <subject>
```

| 类型 | 含义 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修 Bug |
| `docs` | 文档 |
| `style` | 格式 |
| `refactor` | 重构 |
| `perf` | 性能 |
| `test` | 测试 |
| `build` | 构建 |
| `ci` | CI 配置 |
| `chore` | 杂项 |
| `revert` | 回滚 |

```
feat(chart): 支持 X 轴标签截断
fix(sheet): 补回 min-height: 0
docs(readme): 增加英文版
chore(deps): 升级 uCharts 到 v2.5.0
```