<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getSquare, toggleLike, getComments, postComment, deleteComment } from '@/api/square'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const records = ref([])
const total = ref(0)

const query = reactive({
  page: 1,
  size: 10,
  sort: 'time', // time | likes
  mealType: ''
})

const mealTypes = ['早餐', '午餐', '晚餐', '加餐']

// 评论弹窗
const commentVisible = ref(false)
const commentLoading = ref(false)
const currentRecord = ref(null)
const comments = ref([])
const commentInput = ref('')
const replyTo = ref(null) // { commentId, username }

async function loadSquare() {
  loading.value = true
  try {
    const params = { page: query.page, size: query.size, sort: query.sort }
    if (query.mealType) params.mealType = query.mealType
    const data = await getSquare(params)
    records.value = data.records || []
    total.value = data.total || 0
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

async function handleLike(record) {
  try {
    const data = await toggleLike(record.recordId)
    record.liked = data.liked
    record.likeCount = data.likeCount
  } catch (e) {
    /* 拦截器已提示 */
  }
}

/* ============ 评论（分楼） ============ */
async function openComments(record) {
  currentRecord.value = record
  commentVisible.value = true
  replyTo.value = null
  commentInput.value = ''
  await loadComments()
}

async function loadComments() {
  commentLoading.value = true
  try {
    const data = await getComments(currentRecord.value.recordId)
    comments.value = data.comments || []
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    commentLoading.value = false
  }
}

function startReply(comment, isReply = false) {
  // 回复目标：一级评论本身；对二级回复仍然挂在其一级评论下
  replyTo.value = {
    commentId: isReply ? comment.parentId || comment.commentId : comment.commentId,
    username: comment.username
  }
  commentInput.value = `@${comment.username} `
}

function cancelReply() {
  replyTo.value = null
  commentInput.value = ''
}

async function submitComment() {
  const content = commentInput.value.trim()
  if (!content) return
  try {
    await postComment({
      recordId: currentRecord.value.recordId,
      content,
      parentId: replyTo.value?.commentId || null
    })
    ElMessage.success('评论成功')
    commentInput.value = ''
    replyTo.value = null
    currentRecord.value.commentCount++
    loadComments()
  } catch (e) {
    /* 拦截器已提示 */
  }
}

async function handleDeleteComment(commentId) {
  try {
    await deleteComment(commentId)
    ElMessage.success('已删除')
    loadComments()
  } catch (e) {
    /* 拦截器已提示 */
  }
}

function handlePageChange(page) {
  query.page = page
  loadSquare()
}

function mealTagType(mealType) {
  const map = { 早餐: 'success', 午餐: 'primary', 晚餐: 'warning', 加餐: 'info' }
  return map[mealType] || 'info'
}

onMounted(loadSquare)
</script>

<template>
  <div class="square-page">
    <!-- 筛选栏 -->
    <el-card class="page-card">
      <div class="filter-bar">
        <el-radio-group v-model="query.sort" @change="() => { query.page = 1; loadSquare() }">
          <el-radio-button value="time">最新</el-radio-button>
          <el-radio-button value="likes">最热</el-radio-button>
        </el-radio-group>
        <el-select
          v-model="query.mealType"
          clearable
          placeholder="全部餐次"
          style="width: 120px"
          @change="() => { query.page = 1; loadSquare() }"
        >
          <el-option v-for="t in mealTypes" :key="t" :label="t" :value="t" />
        </el-select>
      </div>
    </el-card>

    <!-- 广场卡片流 -->
    <div v-loading="loading" class="feed">
      <el-empty v-if="!loading && !records.length" description="暂无公开记录，快去晒出你的健康饮食吧" />

      <el-card v-for="record in records" :key="record.recordId" class="feed-item">
        <!-- 用户信息 -->
        <div class="feed-header">
          <el-avatar
            :size="40"
            class="feed-avatar"
            @click="router.push(`/user/${record.userId}`)"
          >
            {{ (record.username || 'U').charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="feed-user">
            <span class="feed-username" @click="router.push(`/user/${record.userId}`)">
              {{ record.username }}
            </span>
            <span class="feed-meta">
              <el-tag :type="mealTagType(record.mealType)" size="small">{{ record.mealType }}</el-tag>
              {{ record.createdAt }}
            </span>
          </div>
        </div>

        <!-- 内容 -->
        <div class="feed-body">
          <img v-if="record.imageUrl" :src="record.imageUrl" class="feed-img" alt="" loading="lazy" />
          <div class="feed-food">{{ record.foodName }}</div>
          <div class="feed-cal">
            <span class="nutri-calories">{{ record.calories }} kcal</span>
          </div>
        </div>

        <!-- 互动区 -->
        <div class="feed-actions">
          <el-button
            :type="record.liked ? 'danger' : 'default'"
            text
            @click="handleLike(record)"
          >
            {{ record.liked ? '❤️' : '🤍' }} {{ record.likeCount }}
          </el-button>
          <el-button text @click="openComments(record)">
            💬 {{ record.commentCount }}
          </el-button>
        </div>
      </el-card>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="query.page"
          :page-size="query.size"
          :total="total"
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 评论抽屉（分楼） -->
    <el-drawer
      v-model="commentVisible"
      :title="`评论区 - ${currentRecord?.foodName || ''}`"
      size="420px"
    >
      <div v-loading="commentLoading" class="comment-area">
        <el-empty v-if="!commentLoading && !comments.length" description="还没有评论，来说两句吧" />

        <!-- 一级评论楼层 -->
        <div v-for="comment in comments" :key="comment.commentId" class="comment-floor">
          <div class="comment-item">
            <el-avatar :size="32">{{ (comment.username || 'U').charAt(0).toUpperCase() }}</el-avatar>
            <div class="comment-body">
              <div class="comment-head">
                <span class="comment-username">{{ comment.username }}</span>
                <span class="comment-time">{{ comment.createdAt }}</span>
                <el-button
                  v-if="comment.userId === userStore.userId"
                  text
                  type="danger"
                  size="small"
                  @click="handleDeleteComment(comment.commentId)"
                >
                  删除
                </el-button>
              </div>
              <div class="comment-content">{{ comment.content }}</div>
              <el-button text size="small" @click="startReply(comment)">回复</el-button>

              <!-- 二级回复 -->
              <div v-if="comment.replies?.length" class="reply-list">
                <div v-for="reply in comment.replies" :key="reply.commentId" class="comment-item reply-item">
                  <el-avatar :size="26">{{ (reply.username || 'U').charAt(0).toUpperCase() }}</el-avatar>
                  <div class="comment-body">
                    <div class="comment-head">
                      <span class="comment-username">{{ reply.username }}</span>
                      <span v-if="reply.replyToUsername" class="reply-to">
                        回复 @{{ reply.replyToUsername }}
                      </span>
                      <span class="comment-time">{{ reply.createdAt }}</span>
                      <el-button
                        v-if="reply.userId === userStore.userId"
                        text
                        type="danger"
                        size="small"
                        @click="handleDeleteComment(reply.commentId)"
                      >
                        删除
                      </el-button>
                    </div>
                    <div class="comment-content">{{ reply.content }}</div>
                    <el-button text size="small" @click="startReply(reply, true)">回复</el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 发评论 -->
        <div class="comment-input-bar">
          <div v-if="replyTo" class="replying-tip">
            回复 @{{ replyTo.username }}
            <el-button text size="small" @click="cancelReply">取消</el-button>
          </div>
          <div class="input-row">
            <el-input
              v-model="commentInput"
              placeholder="友善评论，鼓励彼此健康饮食"
              @keyup.enter="submitComment"
            />
            <el-button type="primary" @click="submitComment">发送</el-button>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<style scoped>
.square-page {
  max-width: 720px;
  margin: 0 auto;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.feed {
  margin-top: 16px;
  min-height: 200px;
}

.feed-item {
  margin-bottom: 16px;
}

.feed-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.feed-avatar {
  background: #67c23a;
  color: #fff;
  cursor: pointer;
  flex-shrink: 0;
}

.feed-username {
  font-weight: 600;
  color: #303133;
  cursor: pointer;
}

.feed-username:hover {
  color: #67c23a;
}

.feed-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 2px;
}

.feed-img {
  width: 100%;
  max-height: 320px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 8px;
}

.feed-food {
  font-size: 15px;
  color: #303133;
  margin-bottom: 4px;
}

.feed-cal {
  font-size: 18px;
  font-weight: 700;
}

.feed-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  border-top: 1px solid #f5f5f5;
  padding-top: 8px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

/* 评论区分楼样式 */
.comment-area {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.comment-floor {
  border-bottom: 1px solid #f5f5f5;
  padding: 12px 0;
}

.comment-item {
  display: flex;
  gap: 10px;
}

.comment-body {
  flex: 1;
  min-width: 0;
}

.comment-head {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.comment-username {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.reply-to {
  font-size: 12px;
  color: #409eff;
}

.comment-time {
  font-size: 12px;
  color: #c0c4cc;
}

.comment-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 4px 0;
  word-break: break-word;
}

.reply-list {
  background: #fafafa;
  border-radius: 8px;
  padding: 8px;
  margin-top: 8px;
}

.reply-item {
  margin-bottom: 8px;
}

.reply-item:last-child {
  margin-bottom: 0;
}

.comment-input-bar {
  position: sticky;
  bottom: 0;
  background: #fff;
  padding-top: 12px;
}

.replying-tip {
  font-size: 12px;
  color: #409eff;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.input-row {
  display: flex;
  gap: 8px;
}
</style>
