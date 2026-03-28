# 认证登录模块实现计划

## 需求概述
- 认证方式：JWT Token
- 用户分级：admin（唯一） + 普通用户
- 数据隔离：用户间完全隔离，admin可查看所有数据
- 注册方式：需要审核（admin审核或邀请码）
- Admin初始化：首次启动时引导创建

## 一、后端实现

### 1. 新增依赖
```
python-jose[cryptography]  # JWT处理
passlib[bcrypt]            # 密码哈希
```

### 2. 数据库模型 (`backend/app/models/models.py`)

新增User模型：
```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # "admin" or "user"
    status = Column(String(20), default="pending")  # "pending", "approved", "rejected"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True))
    approved_by = Column(Integer, ForeignKey("users.id"))
```

修改现有模型，添加user_id外键：
- KnowledgeBase: 添加 `user_id` 外键
- ChatSession: 添加 `user_id` 外键

### 3. 配置更新 (`backend/app/config.py`)
```python
# JWT配置
JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
JWT_ALGORITHM: str = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
```

### 4. 认证服务 (`backend/app/services/auth.py`)
- `hash_password()` - 密码哈希
- `verify_password()` - 密码验证
- `create_access_token()` - 创建访问令牌
- `create_refresh_token()` - 创建刷新令牌
- `verify_token()` - 验证令牌
- `get_current_user()` - 获取当前用户依赖

### 5. API路由 (`backend/app/api/auth.py`)

| 端点 | 方法 | 描述 | 权限 |
|------|------|------|------|
| `/api/auth/register` | POST | 用户注册 | 公开 |
| `/api/auth/login` | POST | 用户登录 | 公开 |
| `/api/auth/refresh` | POST | 刷新Token | 已登录 |
| `/api/auth/me` | GET | 获取当前用户信息 | 已登录 |
| `/api/auth/change-password` | PUT | 修改密码 | 已登录 |
| `/api/auth/users` | GET | 获取用户列表 | admin |
| `/api/auth/users/{id}/approve` | PUT | 审核通过用户 | admin |
| `/api/auth/users/{id}/reject` | PUT | 拒绝用户 | admin |
| `/api/auth/init-admin` | POST | 初始化admin账号 | 无用户时 |

### 6. 权限中间件
- `get_current_user()` - 获取当前用户（可选）
- `require_user()` - 要求已登录用户
- `require_admin()` - 要求admin权限

### 7. 修改现有API
为所有需要权限的API添加用户认证：
- 知识库API：按user_id过滤，admin不过滤
- 会话API：按user_id过滤，admin不过滤
- 文件上传：关联user_id

## 二、前端实现

### 1. 新增页面
- `Login.vue` - 登录页面
- `Register.vue` - 注册页面
- `UserManagement.vue` - 用户管理页面（admin专用）
- `InitAdmin.vue` - Admin初始化引导页面

### 2. 路由守卫 (`frontend/src/router/index.ts`)
```typescript
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || 'null')

  // 检查是否需要初始化admin
  if (!user && to.path !== '/init' && to.path !== '/login') {
    const needsInit = await checkNeedsInit()
    if (needsInit) return next('/init')
  }

  // 需要认证的路由
  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

  // admin专用路由
  if (to.meta.requiresAdmin && user?.role !== 'admin') {
    return next('/')
  }

  next()
})
```

### 3. 状态管理
使用简单的响应式状态（无需Pinia/Vuex）：
```typescript
// frontend/src/composables/useAuth.ts
const user = ref<User | null>(null)
const token = ref<string | null>(null)

export function useAuth() {
  return { user, token, login, logout, register, checkAuth }
}
```

### 4. API客户端更新
- 所有请求自动携带Authorization头
- 处理401响应自动跳转登录
- 处理token刷新

### 5. UI组件
- 登录表单
- 注册表单
- 用户管理表格
- Admin初始化向导

## 三、数据库迁移

创建迁移脚本 `backend/scripts/migrate_auth.py`：
1. 创建users表
2. 为knowledge_bases和chat_sessions添加user_id列
3. 迁移现有数据（关联到admin用户或保持公开）

## 四、实现步骤

### 阶段一：后端核心（约8个文件）
1. 更新 `requirements.txt` 添加依赖
2. 更新 `config.py` 添加JWT配置
3. 创建 `models/models.py` 中的User模型
4. 创建 `services/auth.py` 认证服务
5. 创建 `api/auth.py` 认证路由
6. 更新 `main.py` 注册路由
7. 更新 `database.py` 初始化逻辑
8. 修改现有API添加权限过滤

### 阶段二：前端核心（约6个文件）
1. 创建 `composables/useAuth.ts` 认证状态
2. 更新 `api/client.ts` 添加认证API
3. 创建 `views/Login.vue` 登录页面
4. 创建 `views/Register.vue` 注册页面
5. 创建 `views/UserManagement.vue` 用户管理
6. 更新 `router/index.ts` 添加路由守卫

### 阶段三：完善功能
1. Admin初始化引导流程
2. 用户审核功能
3. 密码修改功能
4. Token刷新机制

## 五、安全考虑
- 密码使用bcrypt哈希存储
- JWT使用强密钥（生产环境从环境变量读取）
- Token过期时间合理设置
- 敏感操作需要验证权限
- 防止SQL注入和XSS攻击
