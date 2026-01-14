# 📑 Đặc Tả Yêu Cầu Bài Toán - Backend Developer Assignment

> **Nguồn**: River Flow Solutions, Jsc. 2026  
> **Mục tiêu**: Xây dựng hệ thống **Quản lý Task đa tổ chức** (Multi-organization Task Management) với các tính năng cộng tác và thông báo.

---

## 📋 Mục Lục

1. [Tổng Quan Dự Án](#1-tổng-quan-dự-án)
2. [Yêu Cầu Chức Năng](#2-yêu-cầu-chức-năng)
3. [Use Cases Chi Tiết](#3-use-cases-chi-tiết)
4. [Business Rules](#4-business-rules)
5. [API Endpoints](#5-api-endpoints)
6. [Entity Relationship Diagram](#6-entity-relationship-diagram)
7. [Yêu Cầu Kỹ Thuật](#7-yêu-cầu-kỹ-thuật)
8. [Tiêu Chí Đánh Giá](#8-tiêu-chí-đánh-giá)

---

## 1. Tổng Quan Dự Án

### 1.1 Mô Tả
Xây dựng một hệ thống backend quản lý task theo mô hình phân cấp:
- **Organizations** (Tổ chức) → **Projects** (Dự án) → **Tasks** (Công việc)

### 1.2 Tech Stack Bắt Buộc
| Thành phần          | Công nghệ               |
| ------------------- | ----------------------- |
| Backend Framework   | Python + FastAPI        |
| ORM                 | SQLAlchemy              |
| Database Migrations | Alembic                 |
| Database            | PostgreSQL              |
| Cache/Notifications | Redis                   |
| Authentication      | JWT (PyJWT)             |
| Testing             | pytest                  |
| Deployment          | Docker + docker-compose |
| Reverse Proxy       | Nginx                   |
| Command Runner      | Justfile                |

---

## 2. Yêu Cầu Chức Năng

### 2.1 Quản Lý Tổ Chức & Người Dùng (Organizations & Users)
- Mỗi user thuộc về **một tổ chức**.
- Hệ thống có **3 vai trò (roles)**:
  | Role        | Quyền hạn                                              |
  | ----------- | ------------------------------------------------------ |
  | **Admin**   | Toàn quyền quản lý tổ chức, thêm users, tạo projects   |
  | **Manager** | Tạo projects, quản lý tasks, gán task cho người khác   |
  | **Member**  | Chỉ tham gia projects, tạo/cập nhật tasks của bản thân |

### 2.2 Quản Lý Dự Án (Projects)
- Mỗi project thuộc về **một tổ chức**.
- Có thể thêm/xóa members vào project.
- Chỉ **Admin/Manager** được phép tạo projects.
- **Members** chỉ có thể tham gia projects.

### 2.3 Quản Lý Công Việc (Tasks)
- Các thao tác CRUD (Create, Read, Update, Delete).
- Mỗi task thuộc về **một project**.
- **Các trường dữ liệu**:
  | Field         | Type      | Description                   |
  | ------------- | --------- | ----------------------------- |
  | `title`       | string    | Tiêu đề task                  |
  | `description` | text      | Mô tả chi tiết                |
  | `status`      | enum      | `todo`, `in-progress`, `done` |
  | `priority`    | enum      | `low`, `medium`, `high`       |
  | `due_date`    | datetime  | Hạn hoàn thành                |
  | `assignee`    | FK → User | Người được giao task          |

- **Status workflow**: `todo → in-progress → done` (chỉ đi tiến, không lùi lại)

### 2.4 Cộng Tác (Collaboration)
- Users có thể **bình luận (comment)** trên tasks.
- Users có thể **upload file đính kèm** (lưu local storage).

### 2.5 Thông Báo (Notifications)
User nhận thông báo khi:
- ✅ Được giao một task mới.
- ✅ Task status thay đổi.
- ✅ Có comment mới trên task của họ.

### 2.6 Báo Cáo (Reports)
- Đếm số lượng tasks theo status trong một project.
- Liệt kê các tasks quá hạn (overdue).

---

## 3. Use Cases Chi Tiết

### UC1: Quản Lý Người Dùng (User Management)
| #   | Action          | Actor | Description           |
| --- | --------------- | ----- | --------------------- |
| 1.1 | Register        | Guest | Đăng ký tài khoản mới |
| 1.2 | Login           | Guest | Đăng nhập với JWT     |
| 1.3 | Add User to Org | Admin | Thêm user vào tổ chức |

### UC2: Quản Lý Dự Án (Project Management)
| #   | Action         | Actor         | Description               |
| --- | -------------- | ------------- | ------------------------- |
| 2.1 | Create Project | Admin/Manager | Tạo dự án mới             |
| 2.2 | List Projects  | Any Member    | Xem danh sách dự án       |
| 2.3 | Add Member     | Admin/Manager | Thêm thành viên vào dự án |
| 2.4 | Remove Member  | Admin/Manager | Xóa thành viên khỏi dự án |

### UC3: Quản Lý Task (Task Management)
| #   | Action        | Actor          | Description                                                    |
| --- | ------------- | -------------- | -------------------------------------------------------------- |
| 3.1 | Create Task   | Project Member | Tạo task với title, description, assignee, priority, due_date  |
| 3.2 | Update Status | Project Member | Chuyển status: `todo → in-progress → done`                     |
| 3.3 | List Tasks    | Project Member | Xem tasks với filter (status, assignee, priority) + pagination |
| 3.4 | Update Task   | Project Member | Cập nhật thông tin task                                        |
| 3.5 | Delete Task   | Admin/Manager  | Xóa task                                                       |

### UC4: Cộng Tác (Collaboration)
| #   | Action            | Actor          | Description                                         |
| --- | ----------------- | -------------- | --------------------------------------------------- |
| 4.1 | Add Comment       | Project Member | Thêm comment vào task                               |
| 4.2 | Upload Attachment | Project Member | Upload file đính kèm (max 5MB, tối đa 3 files/task) |

### UC5: Thông Báo (Notifications)
| #   | Action            | Actor | Description                      |
| --- | ----------------- | ----- | -------------------------------- |
| 5.1 | Get Notifications | User  | Lấy danh sách thông báo chưa đọc |
| 5.2 | Mark as Read      | User  | Đánh dấu thông báo đã đọc        |

### UC6: Báo Cáo (Reporting)
| #   | Action               | Actor          | Description                         |
| --- | -------------------- | -------------- | ----------------------------------- |
| 6.1 | Task Count by Status | Project Member | Đếm tasks theo status trong project |
| 6.2 | Overdue Tasks        | Project Member | Lấy danh sách tasks quá hạn         |

---

## 4. Business Rules

| #   | Rule                | Description                                                                      |
| --- | ------------------- | -------------------------------------------------------------------------------- |
| BR1 | Project Membership  | Chỉ thành viên của project mới có thể tạo/cập nhật tasks trong project đó        |
| BR2 | Task Assignment     | Admin/Manager có thể gán task cho người khác; Member chỉ gán cho chính mình      |
| BR3 | Due Date Validation | Due date phải là ngày hôm nay hoặc trong tương lai (không cho phép ngày quá khứ) |
| BR4 | Status Flow         | Status chỉ đi tiến: `todo → in-progress → done`, KHÔNG được lùi lại              |
| BR5 | Attachment Limits   | Mỗi file tối đa 5MB, mỗi task tối đa 3 files đính kèm                            |

---

## 5. API Endpoints

### 5.1 Authentication
| Method | Endpoint                | Description               | Auth |
| ------ | ----------------------- | ------------------------- | ---- |
| `POST` | `/api/v1/auth/register` | Đăng ký tài khoản         | ❌    |
| `POST` | `/api/v1/auth/login`    | Đăng nhập, nhận JWT token | ❌    |
| `POST` | `/api/v1/auth/refresh`  | Refresh JWT token         | ✅    |

### 5.2 Users
| Method | Endpoint           | Description                 | Auth | Role  |
| ------ | ------------------ | --------------------------- | ---- | ----- |
| `GET`  | `/api/v1/users/me` | Lấy thông tin user hiện tại | ✅    | Any   |
| `PUT`  | `/api/v1/users/me` | Cập nhật thông tin user     | ✅    | Any   |
| `GET`  | `/api/v1/users`    | Liệt kê users trong tổ chức | ✅    | Admin |

### 5.3 Organizations
| Method   | Endpoint                                     | Description            | Auth | Role  |
| -------- | -------------------------------------------- | ---------------------- | ---- | ----- |
| `GET`    | `/api/v1/organizations`                      | Lấy thông tin tổ chức  | ✅    | Any   |
| `POST`   | `/api/v1/organizations/users`                | Thêm user vào tổ chức  | ✅    | Admin |
| `DELETE` | `/api/v1/organizations/users/{user_id}`      | Xóa user khỏi tổ chức  | ✅    | Admin |
| `PUT`    | `/api/v1/organizations/users/{user_id}/role` | Thay đổi role của user | ✅    | Admin |

### 5.4 Projects
| Method   | Endpoint                                          | Description                 | Auth | Role           |
| -------- | ------------------------------------------------- | --------------------------- | ---- | -------------- |
| `POST`   | `/api/v1/projects`                                | Tạo project mới             | ✅    | Admin/Manager  |
| `GET`    | `/api/v1/projects`                                | Liệt kê projects            | ✅    | Any            |
| `GET`    | `/api/v1/projects/{project_id}`                   | Chi tiết project            | ✅    | Project Member |
| `PUT`    | `/api/v1/projects/{project_id}`                   | Cập nhật project            | ✅    | Admin/Manager  |
| `DELETE` | `/api/v1/projects/{project_id}`                   | Xóa project                 | ✅    | Admin          |
| `POST`   | `/api/v1/projects/{project_id}/members`           | Thêm member vào project     | ✅    | Admin/Manager  |
| `DELETE` | `/api/v1/projects/{project_id}/members/{user_id}` | Xóa member khỏi project     | ✅    | Admin/Manager  |
| `GET`    | `/api/v1/projects/{project_id}/members`           | Liệt kê members của project | ✅    | Project Member |

### 5.5 Tasks
| Method   | Endpoint                              | Description                           | Auth | Role           |
| -------- | ------------------------------------- | ------------------------------------- | ---- | -------------- |
| `POST`   | `/api/v1/projects/{project_id}/tasks` | Tạo task mới                          | ✅    | Project Member |
| `GET`    | `/api/v1/projects/{project_id}/tasks` | Liệt kê tasks (có filter, pagination) | ✅    | Project Member |
| `GET`    | `/api/v1/tasks/{task_id}`             | Chi tiết task                         | ✅    | Project Member |
| `PUT`    | `/api/v1/tasks/{task_id}`             | Cập nhật task                         | ✅    | Project Member |
| `PATCH`  | `/api/v1/tasks/{task_id}/status`      | Cập nhật status                       | ✅    | Project Member |
| `DELETE` | `/api/v1/tasks/{task_id}`             | Xóa task                              | ✅    | Admin/Manager  |

**Query Parameters cho List Tasks:**
| Parameter     | Type   | Description                           |
| ------------- | ------ | ------------------------------------- |
| `status`      | string | Filter: `todo`, `in-progress`, `done` |
| `priority`    | string | Filter: `low`, `medium`, `high`       |
| `assignee_id` | int    | Filter theo người được giao           |
| `page`        | int    | Số trang (default: 1)                 |
| `per_page`    | int    | Số items/trang (default: 10)          |

### 5.6 Comments
| Method   | Endpoint                           | Description      | Auth | Role                |
| -------- | ---------------------------------- | ---------------- | ---- | ------------------- |
| `POST`   | `/api/v1/tasks/{task_id}/comments` | Thêm comment     | ✅    | Project Member      |
| `GET`    | `/api/v1/tasks/{task_id}/comments` | Liệt kê comments | ✅    | Project Member      |
| `DELETE` | `/api/v1/comments/{comment_id}`    | Xóa comment      | ✅    | Comment Owner/Admin |

### 5.7 Attachments
| Method   | Endpoint                              | Description           | Auth | Role           |
| -------- | ------------------------------------- | --------------------- | ---- | -------------- |
| `POST`   | `/api/v1/tasks/{task_id}/attachments` | Upload file (max 5MB) | ✅    | Project Member |
| `GET`    | `/api/v1/tasks/{task_id}/attachments` | Liệt kê attachments   | ✅    | Project Member |
| `GET`    | `/api/v1/attachments/{attachment_id}` | Download file         | ✅    | Project Member |
| `DELETE` | `/api/v1/attachments/{attachment_id}` | Xóa attachment        | ✅    | Uploader/Admin |

### 5.8 Notifications
| Method  | Endpoint                                       | Description                  | Auth |
| ------- | ---------------------------------------------- | ---------------------------- | ---- |
| `GET`   | `/api/v1/notifications`                        | Lấy thông báo (unread first) | ✅    |
| `PATCH` | `/api/v1/notifications/{notification_id}/read` | Đánh dấu đã đọc              | ✅    |
| `PATCH` | `/api/v1/notifications/read-all`               | Đánh dấu tất cả đã đọc       | ✅    |

### 5.9 Reports
| Method | Endpoint                                              | Description           | Auth | Role           |
| ------ | ----------------------------------------------------- | --------------------- | ---- | -------------- |
| `GET`  | `/api/v1/projects/{project_id}/reports/task-count`    | Đếm tasks theo status | ✅    | Project Member |
| `GET`  | `/api/v1/projects/{project_id}/reports/overdue-tasks` | Lấy tasks quá hạn     | ✅    | Project Member |

### 5.10 Health Check
| Method | Endpoint               | Description                  | Auth |
| ------ | ---------------------- | ---------------------------- | ---- |
| `GET`  | `/api/v1/health`       | Kiểm tra health của hệ thống | ❌    |
| `GET`  | `/api/v1/health/db`    | Kiểm tra kết nối database    | ❌    |
| `GET`  | `/api/v1/health/redis` | Kiểm tra kết nối Redis       | ❌    |

---

## 6. Entity Relationship Diagram

### 6.1 Sơ Đồ ER

```
┌─────────────────────┐       ┌─────────────────────┐
│    ORGANIZATION     │       │        USER         │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │       │ id (PK)             │
│ name                │       │ email               │
│ created_at          │──────<│ password_hash       │
│ updated_at          │   1:N │ full_name           │
└─────────────────────┘       │ role (enum)         │
                              │ organization_id (FK)│
                              │ created_at          │
                              │ updated_at          │
                              └──────────┬──────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
         ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
         │  PROJECT_MEMBER  │  │   NOTIFICATION   │  │     COMMENT      │
         │  (Junction Table)│  ├──────────────────┤  ├──────────────────┤
         ├──────────────────┤  │ id (PK)          │  │ id (PK)          │
         │ project_id (FK)  │  │ user_id (FK)     │  │ content          │
         │ user_id (FK)     │  │ type (enum)      │  │ task_id (FK)     │
         │ joined_at        │  │ message          │  │ user_id (FK)     │
         └────────┬─────────┘  │ is_read          │  │ created_at       │
                  │            │ created_at       │  └──────────────────┘
                  │            └──────────────────┘           ▲
                  │                                           │
                  ▼                                           │
┌─────────────────────┐       ┌─────────────────────┐        │
│      PROJECT        │       │        TASK         │        │
├─────────────────────┤       ├─────────────────────┤        │
│ id (PK)             │       │ id (PK)             │        │
│ name                │──────<│ title               │────────┘
│ description         │   1:N │ description         │
│ organization_id (FK)│       │ status (enum)       │
│ created_by (FK)     │       │ priority (enum)     │
│ created_at          │       │ due_date            │
│ updated_at          │       │ project_id (FK)     │
└─────────────────────┘       │ assignee_id (FK)    │
                              │ created_by (FK)     │
                              │ created_at          │
                              │ updated_at          │
                              └──────────┬──────────┘
                                         │
                                         │ 1:N
                                         ▼
                              ┌─────────────────────┐
                              │     ATTACHMENT      │
                              ├─────────────────────┤
                              │ id (PK)             │
                              │ filename            │
                              │ filepath            │
                              │ file_size           │
                              │ mime_type           │
                              │ task_id (FK)        │
                              │ uploaded_by (FK)    │
                              │ created_at          │
                              └─────────────────────┘
```

### 6.2 Chi Tiết Các Entity

#### **Organization**
| Column       | Type         | Constraints      | Description        |
| ------------ | ------------ | ---------------- | ------------------ |
| `id`         | UUID/INT     | PK, AUTO         | ID tổ chức         |
| `name`       | VARCHAR(255) | NOT NULL, UNIQUE | Tên tổ chức        |
| `created_at` | TIMESTAMP    | DEFAULT NOW()    | Thời điểm tạo      |
| `updated_at` | TIMESTAMP    | ON UPDATE NOW()  | Thời điểm cập nhật |

#### **User**
| Column            | Type         | Constraints      | Description                  |
| ----------------- | ------------ | ---------------- | ---------------------------- |
| `id`              | UUID/INT     | PK, AUTO         | ID người dùng                |
| `email`           | VARCHAR(255) | NOT NULL, UNIQUE | Email đăng nhập              |
| `password_hash`   | VARCHAR(255) | NOT NULL         | Password đã hash             |
| `full_name`       | VARCHAR(255) | NOT NULL         | Họ tên                       |
| `role`            | ENUM         | NOT NULL         | `admin`, `manager`, `member` |
| `organization_id` | FK           | NOT NULL         | Tham chiếu Organization      |
| `created_at`      | TIMESTAMP    | DEFAULT NOW()    | Thời điểm tạo                |
| `updated_at`      | TIMESTAMP    | ON UPDATE NOW()  | Thời điểm cập nhật           |

#### **Project**
| Column            | Type         | Constraints     | Description             |
| ----------------- | ------------ | --------------- | ----------------------- |
| `id`              | UUID/INT     | PK, AUTO        | ID dự án                |
| `name`            | VARCHAR(255) | NOT NULL        | Tên dự án               |
| `description`     | TEXT         | NULLABLE        | Mô tả dự án             |
| `organization_id` | FK           | NOT NULL        | Tham chiếu Organization |
| `created_by`      | FK           | NOT NULL        | User tạo project        |
| `created_at`      | TIMESTAMP    | DEFAULT NOW()   | Thời điểm tạo           |
| `updated_at`      | TIMESTAMP    | ON UPDATE NOW() | Thời điểm cập nhật      |

#### **ProjectMember** (Junction Table)
| Column       | Type      | Constraints   | Description        |
| ------------ | --------- | ------------- | ------------------ |
| `project_id` | FK        | PK, NOT NULL  | Tham chiếu Project |
| `user_id`    | FK        | PK, NOT NULL  | Tham chiếu User    |
| `joined_at`  | TIMESTAMP | DEFAULT NOW() | Thời điểm join     |

#### **Task**
| Column        | Type         | Constraints                | Description                   |
| ------------- | ------------ | -------------------------- | ----------------------------- |
| `id`          | UUID/INT     | PK, AUTO                   | ID task                       |
| `title`       | VARCHAR(255) | NOT NULL                   | Tiêu đề                       |
| `description` | TEXT         | NULLABLE                   | Mô tả chi tiết                |
| `status`      | ENUM         | NOT NULL, DEFAULT 'todo'   | `todo`, `in-progress`, `done` |
| `priority`    | ENUM         | NOT NULL, DEFAULT 'medium' | `low`, `medium`, `high`       |
| `due_date`    | DATE         | NULLABLE                   | Hạn hoàn thành                |
| `project_id`  | FK           | NOT NULL                   | Tham chiếu Project            |
| `assignee_id` | FK           | NULLABLE                   | User được giao task           |
| `created_by`  | FK           | NOT NULL                   | User tạo task                 |
| `created_at`  | TIMESTAMP    | DEFAULT NOW()              | Thời điểm tạo                 |
| `updated_at`  | TIMESTAMP    | ON UPDATE NOW()            | Thời điểm cập nhật            |

**Indexes:**
- `idx_task_project_id` trên `project_id`
- `idx_task_assignee_id` trên `assignee_id`
- `idx_task_status` trên `status`
- `idx_task_due_date` trên `due_date`

#### **Comment**
| Column       | Type      | Constraints   | Description       |
| ------------ | --------- | ------------- | ----------------- |
| `id`         | UUID/INT  | PK, AUTO      | ID comment        |
| `content`    | TEXT      | NOT NULL      | Nội dung comment  |
| `task_id`    | FK        | NOT NULL      | Tham chiếu Task   |
| `user_id`    | FK        | NOT NULL      | User viết comment |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Thời điểm tạo     |

#### **Attachment**
| Column        | Type         | Constraints   | Description           |
| ------------- | ------------ | ------------- | --------------------- |
| `id`          | UUID/INT     | PK, AUTO      | ID attachment         |
| `filename`    | VARCHAR(255) | NOT NULL      | Tên file gốc          |
| `filepath`    | VARCHAR(500) | NOT NULL      | Đường dẫn lưu trữ     |
| `file_size`   | INT          | NOT NULL      | Kích thước (bytes)    |
| `mime_type`   | VARCHAR(100) | NOT NULL      | Loại file (MIME type) |
| `task_id`     | FK           | NOT NULL      | Tham chiếu Task       |
| `uploaded_by` | FK           | NOT NULL      | User upload file      |
| `created_at`  | TIMESTAMP    | DEFAULT NOW() | Thời điểm upload      |

#### **Notification**
| Column            | Type      | Constraints   | Description                                        |
| ----------------- | --------- | ------------- | -------------------------------------------------- |
| `id`              | UUID/INT  | PK, AUTO      | ID notification                                    |
| `user_id`         | FK        | NOT NULL      | User nhận thông báo                                |
| `type`            | ENUM      | NOT NULL      | `task_assigned`, `status_changed`, `comment_added` |
| `message`         | TEXT      | NOT NULL      | Nội dung thông báo                                 |
| `related_task_id` | FK        | NULLABLE      | Task liên quan                                     |
| `is_read`         | BOOLEAN   | DEFAULT FALSE | Trạng thái đã đọc                                  |
| `created_at`      | TIMESTAMP | DEFAULT NOW() | Thời điểm tạo                                      |

**Lưu ý**: Notifications có thể được cache trong Redis để tăng performance.

### 6.3 Mối Quan Hệ (Relationships)

| Relationship           | Type | Description                           |
| ---------------------- | ---- | ------------------------------------- |
| Organization → User    | 1:N  | Một tổ chức có nhiều users            |
| Organization → Project | 1:N  | Một tổ chức có nhiều projects         |
| Project ↔ User         | N:M  | Thông qua bảng `ProjectMember`        |
| Project → Task         | 1:N  | Một project có nhiều tasks            |
| User → Task (assignee) | 1:N  | Một user có thể được giao nhiều tasks |
| User → Task (creator)  | 1:N  | Một user có thể tạo nhiều tasks       |
| Task → Comment         | 1:N  | Một task có nhiều comments            |
| Task → Attachment      | 1:N  | Một task có tối đa 3 attachments      |
| User → Notification    | 1:N  | Một user có nhiều notifications       |

---

## 7. Yêu Cầu Kỹ Thuật

### 7.1 MCP Server (Model Context Protocol)
- Chuyển đổi FastAPI backend thành MCP server.
- Sử dụng phương pháp **auto-conversion** (tự động expose tất cả endpoints thành MCP tools).
- **Không** định nghĩa manual cho từng tool.
- Test MCP server bằng Task AI Agent.

### 7.2 Task AI Agent
- Tích hợp với ít nhất một LLM provider (Groq, OpenAI, Anthropic, etc.).
- Khả năng:
  - Hiểu natural language requests về tasks.
  - Tự động tạo, cập nhật, query tasks thông qua MCP tools.
  - Đưa ra suggestions và recommendations.
  - Phân tích dữ liệu task và tạo insights.
  - Xử lý multi-step operations.

### 7.3 Testing
- Sử dụng pytest với test containers hoặc mocks.
- Test coverage ≥ 70%.
- Test cho: Auth, Users, Organizations, Projects, Tasks, MCP, Agent.

### 7.4 Deployment
- Dockerized với docker-compose.
- Bao gồm: FastAPI + PostgreSQL + Redis + Nginx.
- Health check endpoints.
- Environment variables qua `.env`.

---

## 8. Tiêu Chí Đánh Giá

### Tổng điểm: 100

| Mục                         | Điểm | Chi tiết                                          |
| --------------------------- | ---- | ------------------------------------------------- |
| **D1. Core Requirements**   | 40   |                                                   |
| Database schema             | 8    | Relations, constraints, indexes                   |
| JWT auth + RBAC             | 8    | Admin/Manager/Member roles                        |
| CRUD Operations             | 12   | Organizations, Projects, Tasks + business rules   |
| Workflow + Collaboration    | 8    | Status flow, comments, attachments, notifications |
| Reports                     | 4    | Task counts, overdue tasks                        |
| **D2. MCP & AI Agent**      | 20   |                                                   |
| MCP auto-conversion         | 6    | Không manual definitions                          |
| AI Agent tích hợp           | 4    | Kết nối MCP server                                |
| MCP testing via Agent       | 3    | CRUD operations                                   |
| LLM integration             | 3    | Ít nhất 1 provider                                |
| Natural language processing | 2    | Interpret và execute                              |
| Agent features              | 2    | Ít nhất 3 features                                |
| **D3. Code Quality**        | 20   |                                                   |
| Error handling, logging     | 6    | Centralized, consistent                           |
| Configuration, pagination   | 4    | `.env`, list endpoints                            |
| Test coverage               | 10   | ≥ 70%                                             |
| **D4. Deployment & Docs**   | 20   |                                                   |
| Dockerized deployment       | 10   | Nginx, PostgreSQL, Redis                          |
| Health checks, env vars     | 4    |                                                   |
| README, Swagger UI          | 6    |                                                   |

---

## 📁 Cấu Trúc Thư Mục Dự Án

```
be-assignment/
├── app/                      # Main application
│   ├── main.py               # FastAPI entry point
│   ├── config.py             # Configuration
│   ├── core/                 # Security, Auth, Exceptions, Logging
│   ├── db/                   # Database setup
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic schemas
│   ├── api/v1/               # API routes
│   ├── services/             # Business logic
│   ├── utils/                # Utilities
│   ├── mcp/                  # MCP Server
│   └── agent/                # Task AI Agent
├── migrations/               # Alembic migrations
├── tests/                    # Test files
├── nginx/                    # Nginx config
├── docs/                     # ER diagram, System design
├── storage/uploads/          # File attachments
├── docker-compose.yml
├── Dockerfile
├── Justfile
└── requirements.txt
```

---

> **Lưu ý**: File này được tạo để đặc tả chi tiết yêu cầu bài toán. Vui lòng tham khảo file `README.md` gốc để xem hướng dẫn nộp bài và các lưu ý khác.
