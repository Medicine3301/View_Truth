from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS
import aiomysql
import jwt
import bcrypt
import uuid
from datetime import datetime, timedelta


# 創建Sanic應用
app = Sanic("auth_app")
# 啟用CORS支持
CORS(app)

# JWT配置
SECRET_KEY = "therealeyecanseethetruth"

# 數據庫配置
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "takming",
    "db": "new_community",
    "charset": "utf8mb4",
}


# 在服務器啟動前創建數據庫連接池
@app.listener("before_server_start")
async def setup_db(app, loop):
    app.ctx.pool = await aiomysql.create_pool(**DB_CONFIG, loop=loop, autocommit=True)


# 輔助函數：根據用戶名查詢用戶
async def get_user_by_username(pool, username):
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM users WHERE una = %s", (username,))
            return await cur.fetchone()
    
#輔助函數:查詢貼文最新的紀錄(貼文用)
async def get_latest_comm_id(pool):
    """
    查詢最新的 max_id_id。
    """
    query = "SELECT MAX(CAST(SUBSTRING(comm_id, 3) AS UNSIGNED)) AS max_id FROM comments"

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query)
            result = await cur.fetchone()
            return result[0] if result[0] is not None else 0  # Handle case when no records exist



# 註冊路由
@app.post("/api/register")
async def register(request):
    """用戶註冊API

    接收：
    - name: 用戶名
    - email: 郵箱
    - password: 密碼
    - sex: 性別
    - age: 年齡
    """
    try:
        data = request.json

        # 檢查用戶名是否已存在
        existing_user = await get_user_by_username(app.ctx.pool, data["name"])
        if existing_user:
            return json({"error": "用戶名已存在"}, status=400)

        # 生成唯一用戶ID
        uid = str(uuid.uuid4())

        # 密碼加密
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(data["password"].encode(), salt)
        # 將收到的 ISO 格式日期轉換為 'YYYY-MM-DD'
        iso_birthday = data["birthday"]
        birthday_date = datetime.fromisoformat(
            iso_birthday
        ).date()  # 使用 datetime 類的 fromisoformat 方法
        # 插入用戶數據
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO users (uid, una, birthday, usex, email, passwd)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """,
                    (
                        uid,
                        data["name"],
                        birthday_date,
                        data["sex"],
                        data["email"],
                        hashed_password.decode(),
                    ),
                )

        return json({"message": "註冊成功"}, status=201)

    except Exception as e:
        return json({"error": str(e)}, status=400)
@app.post("/api/post/comment/create")
async def PostCommentAdd(request):
    """用戶新增留言API
    接收：
    - uid:用戶編號
    - una:用戶名
    - title:標題
    - comm_id:貼文表編號
    - content :內容
    - pid :貼文編號
    """
    try:
        data = request.json
        # 獲取最新 news_id 並產生新 ID
        latest_news_id = await get_latest_comm_id(app.ctx.pool) + 1
        next_id = f"RP{latest_news_id}"  # 格式化
        
        # 插入用戶數據
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO comments (pid, title, comm_id, uid, una, content)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        data["pid"],
                        data["title"],
                        next_id,
                        data["uid"],
                        data["una"],
                        data["content"]
                    ),
                )
                await conn.commit()  # Ensure changes are committed

        return json({"message": "留言成功"}, status=201)

    except Exception as e:
        print(str(e))
        return json({"error": str(e)}, status=400)
        

# 登入路由
@app.post("/api/login")
async def login(request):
    """用戶登入API

    接收：
    - username: 用戶名
    - password: 密碼
    """
    try:
        data = request.json
        # 查詢用戶
        user = await get_user_by_username(app.ctx.pool, data["username"])

        if not user:
            return json({"error": "用戶不存在"}, status=404)

        # 驗證密碼
        if not bcrypt.checkpw(data["password"].encode(), user["passwd"].encode()):
            return json({"error": "密碼錯誤"}, status=401)

        # 生成JWT token
        token = jwt.encode(
            {
                "uid": user["uid"],
                "exp": datetime.utcnow() + timedelta(days=1),  # token有效期1天
            },
            SECRET_KEY,
            algorithm="HS256",
        )

        return json(
            {
                "token": token,
                "user": {
                    "uid": user["uid"],
                    "una": user["una"],
                    "email": user["email"],
                    "role": user["role"],
                },
            }
        )

    except Exception as e:
        return json({"error": str(e)}, status=400)


# Token驗證路由
@app.get("/api/verify")
async def verify(request):
    """驗證token有效性API"""
    try:
        # 從header中獲取token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        # 解碼token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # 查詢用戶信息
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    "SELECT uid, una, email ,role FROM users WHERE uid = %s",
                    (payload["uid"],),
                )
                user = await cur.fetchone()

                if not user:
                    return json({"error": "用戶不存在"}, status=404)

                return json({"user": user})

    except jwt.ExpiredSignatureError:
        return json({"error": "Token已過期"}, status=401)
    except jwt.InvalidTokenError:
        return json({"error": "無效的Token"}, status=401)
    except Exception as e:
        return json({"error": str(e)}, status=400)
    # 查詢特定用戶信息的API


@app.get("/api/user/<uid>")
async def get_user_info(request, uid):
    """獲取特定用戶信息API"""
    try:
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    "SELECT uid, una, email, role,birthday,usex FROM users WHERE uid = %s",
                    (uid,),
                )
                user = await cur.fetchone()
                if not user:
                    return json({"error": "用戶不存在"}, status=404)
                # 處理 datetime
                user = dict(user)
                user["birthday"] = (
                    user["birthday"].isoformat() if user["birthday"] else None
                )

                return json({"user": user}, status=200)
    except Exception as e:
        return json({"error": str(e)}, status=400)


@app.get("/api/community/all")
async def get_all_communities(request):
    """獲取所有社群信息的 API"""
    try:
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    "SELECT cid, cna, descr, post_count,last_update FROM community"
                )
                communities = await cur.fetchall()

                if not communities:
                    return json({"error": "沒有找到任何社群"}, status=404)

                # 處理每個社群的數據
                response = [
                    {
                        "cid": community["cid"],
                        "cna": community["cna"],
                        "descr": community["descr"],
                        "post_count": community["post_count"],
                        "last_update": (
                            community["last_update"].isoformat()
                            if community["last_update"]
                            else None
                        ),
                    }
                    for community in communities
                ]

                return json({"communities": response}, status=200)
    except Exception as e:
        print(f"Error in get_all_communities: {str(e)}")
        return json({"error": str(e)}, status=400)


@app.get("/api/community/<cid>")
async def get_community_info(request, cid):
    try:
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                print(f"查詢社群ID: {cid}")
                await cur.execute(
                    "SELECT cid, cna, descr, post_count,last_update FROM community WHERE cid = %s",
                    (cid,),
                )
                community = await cur.fetchone()
                if not community:
                    return json({"error": "社群不存在"}, status=404)

                # 處理 datetime
                community = dict(community)
                community["last_update"] = (
                    community["last_update"].isoformat()
                    if community["last_update"]
                    else None
                )

                return json({"community": community}, status=200)
    except Exception as e:
        print(f"Error in get_community_info: {str(e)}")
        return json({"error": str(e)}, status=400)


@app.get("/api/posts/<cid>")
async def get_all_post(request, cid):
    """獲取所有社群貼文信息的 API"""
    try:
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    "SELECT pid, cid, uid, una,title,content,comm_count,crea_date FROM post where cid=%s",
                    (cid,),
                ),
                posts = await cur.fetchall()

                if not posts:
                    return json({"error": "找尋不到任何貼文"}, status=404)

                # 處理每個社群的數據
                response = [
                    {
                        "pid": post["pid"],
                        "cid": post["cid"],
                        "uid": post["uid"],
                        "una": post["una"],
                        "title": post["title"],
                        "content": post["content"],
                        "comm_count": post["comm_count"],
                        "crea_date": (
                            post["crea_date"].isoformat() if post["crea_date"] else None
                        ),
                    }
                    for post in posts
                ]

                return json({"posts": response}, status=200)
    except Exception as e:
        print(f"Error in get_all_posts: {str(e)}")
        return json({"error": str(e)}, status=400)


@app.get("/api/post/<pid>")
async def get_post_info(request, pid):
    """獲取社群貼文信息的 API"""
    try:
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    "SELECT pid, cid, uid, una,title,content,comm_count,crea_date FROM post where pid=%s",
                    (pid,),
                ),
                post = await cur.fetchone()

                if not post:
                    return json({"error": "找尋不到該貼文"}, status=404)

                # 處理 datetime轉換格式
                post = dict(post)
                post["crea_date"] = (
                    post["crea_date"].isoformat() if post["crea_date"] else None
                )

                return json({"post": post}, status=200)
    except Exception as e:
        print(f"Error in get_post_info: {str(e)}")
        return json({"error": str(e)}, status=400)


@app.get("/api/comment/<pid>")
async def get_all_comment(request, pid):
    """獲取所有貼文留言信息的 API"""
    try:
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    "SELECT pid,uid,una,comm_id,nid,title,content,crea_date FROM comments where pid=%s",
                    (pid,),
                ),
                comments = await cur.fetchall()

                if not comments:
                    return json({"error": "找尋不到任何留言"}, status=404)

                # 處理每個留言的數據
                response = [
                    {
                        "pid": comment["pid"],
                        "uid": comment["uid"],
                        "una": comment["una"],
                        "comm_id": comment["comm_id"],
                        "nid": comment["nid"],
                        "title": comment["title"],
                        "content": comment["content"],
                        "crea_date": (
                            comment["crea_date"].isoformat()
                            if comment["crea_date"]
                            else None
                        ),
                    }
                    for comment in comments
                ]

                return json({"comments": response}, status=200)
    except Exception as e:
        print(f"Error in get_all_comments: {str(e)}")
        return json({"error": str(e)}, status=400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
