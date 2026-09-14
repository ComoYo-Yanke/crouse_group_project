# Git 日常开发速查手册

> 拿上就能复制粘贴。假设远程仓库为 `origin`，主分支为 `main`。

---

## 一、最常用（背下来）

```bash
# 看当前状态
git status

# 拉取 main 最新
git checkout main && git pull

# 开新功能分支
git checkout -b feature/xxx

# 提交
git add .
git commit -m "feat: xxx"

# 推送
git push -u origin feature/xxx
```

---

## 二、分支操作

### 查看分支

```bash
git branch                  # 本地分支
git branch -r               # 远程分支
git branch -a               # 全部
git branch -vv              # 本地 + 跟踪的远程 + 最后 commit
```

### 切换分支

```bash
git checkout main           # 切到 main
git switch main             # 同上（新语法，推荐）
git checkout -              # 切回上一个分支
```



### 创建并切换

```bash
git checkout -b feature/xxx           # 从当前分支切出
git switch -c feature/xxx             # 同上（新语法）
git checkout -b feature/xxx origin/main   # 从远程 main 切出
```



### 删除分支

```bash
git branch -d feature/xxx             # 本地（已合并）
git branch -D feature/xxx             # 本地（强制，未合并也删）
git push origin --delete feature/xxx  # 远程
```



### 重命名分支

```bash
git branch -m old-name new-name       # 本地
git push origin --delete old-name     # 删远程旧名
git push -u origin new-name           # 推远程新名
```

---



## 三、拉取分支



### 场景 1：远程已有分支，本地要拉下来

```bash
git fetch origin                      # 拉取所有远程信息
git checkout feature/xxx              # 自动跟踪 origin/feature/xxx
# 或显式：
git checkout -b feature/xxx origin/feature/xxx
```

