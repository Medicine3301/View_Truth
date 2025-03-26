import base64
from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS
import aiomysql
import jwt
import bcrypt
import uuid
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#郵件認證的函式導入
from back.mail import EmailVerifier



app = Sanic("auth_app")
CORS(app)
#token
SECRET_KEY = "therealeyecanseethetruth"
#db資訊
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456",
    "db": "new_community",
    "charset": "utf8mb4",
    "port": 3306
}

app.static('/static', './static')
@app.listener("before_server_start")
#set db
async def setup_db(app, loop):
    app.ctx.pool = await aiomysql.create_pool(**DB_CONFIG, loop=loop, autocommit=True,maxsize=10 )
#輔助程式-抓用戶資料
async def get_user_by_username(pool, username):
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM users WHERE una = %s", (username,))
            return await cur.fetchone()
#輔助程式-抓最後一個資料
async def get_latest_id(pool, table, id_field, prefix):
    """通用的 ID 獲取函數"""
    query = f"SELECT MAX(CAST(SUBSTRING({id_field}, {len(prefix) + 1}) AS UNSIGNED)) AS max_id FROM {table}"
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query)
            result = await cur.fetchone()
            return result[0] if result[0] is not None else 0
#insert 用
async def get_latest_comm_id(pool):
    return await get_latest_id(pool, "comments", "comm_id", "RP")

async def get_latest_ncomm_id(pool):
    return await get_latest_id(pool, "comments", "comm_id", "RN")

async def get_latest_post_id(pool):
    return await get_latest_id(pool, "post", "pid", "P")

# 在 register 路由中加入驗證碼驗證
@app.post("/api/register")
async def register(request):
    try:
        data = request.json
        if not all(key in data for key in ["name", "email", "password", "sex", "birthday", "verificationCode"]):
            return json({"error": "缺少必要欄位"}, status=400)

        # 驗證驗證碼
        email = data["email"]
        verification_code = data["verificationCode"]
        verifier = EmailVerifier(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            sender_email="acr3214@gmail.com",
            sender_password="opvb zvru aarc oqqn"
        )
        
        success, message = verifier.verify_code(email, verification_code)
        if not success:
            return json({"error": message}, status=400)

        # 如果驗證成功，繼續註冊流程
        existing_user = await get_user_by_username(app.ctx.pool, data["name"])
        if existing_user:
            return json({"error": "用戶名已存在"}, status=400)

        uid = str(uuid.uuid4())
        hashed_password = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())
        birthday_date = datetime.fromisoformat(data["birthday"]).date()

        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO users (uid, una, birthday, usex, email, passwd)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (uid, data["name"], birthday_date, data["sex"], 
                     data["email"], hashed_password.decode())
                )
        return json({"message": "註冊成功", "uid": uid}, status=201)

    except KeyError as e:
        return json({"error": f"缺少必要欄位: {str(e)}"}, status=400)
    except ValueError as e:
        return json({"error": f"資料格式錯誤: {str(e)}"}, status=400)
    except Exception as e:
        return json({"error": f"服務器錯誤: {str(e)}"}, status=500)

# 修改發送驗證碼的函數
@app.post("/api/send_verification_code")
async def send_verification_code(request):
    try:
        data = request.json
        if "email" not in data:
            return json({"error": "缺少必要欄位"}, status=400)
        
        # 檢查郵箱是否已經註冊
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT COUNT(*) FROM users WHERE email = %s", (data["email"],))
                result = await cur.fetchone()
                if result[0] > 0:
                    return json({"error": "此郵箱已被註冊"}, status=400)

        # 發送驗證碼
        verifier = EmailVerifier(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            sender_email="acr3214@gmail.com",
            sender_password="opvb zvru aarc oqqn"
        )
        
        success, message = verifier.send_verification_email(data["email"])
        
        if success:
            return json({"message": "驗證碼已發送"}, status=200)
        else:
            return json({"error": message}, status=400)

    except Exception as e:
        return json({"error": f"服務器錯誤: {str(e)}"}, status=500)

@app.post("/api/post/comment/create")
async def post_comment_add(request):
    try:
        data = request.json
        required_fields = ["pid", "title", "uid", "una", "content"]
        if not all(key in data for key in required_fields):
            return json({"error": "缺少必要欄位"}, status=400)

        latest_id = await get_latest_comm_id(app.ctx.pool)
        next_id = f"RP{latest_id + 1}"

        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO comments (pid, title, comm_id, uid, una, content)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (data["pid"], data["title"], next_id, 
                     data["uid"], data["una"], data["content"])
                )
                

        return json({
            "message": "留言成功",
            "comm_id": next_id
        }, status=201)

    except Exception as e:
        return json({"error": f"服務器錯誤: {str(e)}"}, status=500)

#收藏新增
@app.post("/api/favorites/add")
async def favorite_add(request):
    try:
        data = request.json
        required_fields = ["pid","uid"]
        if not all(key in data for key in required_fields):
            return json({"error": "缺少必要欄位"}, status=400)

        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO collect (pid, uid)
                    VALUES (%s, %s)
                    """,
                    (data["pid"],data["uid"]) )

        return json({
            "message": "收藏成功",
        }, status=201)

    except Exception as e:
        return json({"error": f"服務器錯誤: {str(e)}"}, status=500)
#收藏刪除  
@app.delete("/api/favorites/remove")
async def favorite_delete(request):
    try:
        data = request.json
        required_fields = ["pid","uid"]
        if not all(key in data for key in required_fields):
            return json({"error": "缺少必要欄位"}, status=400)

        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    DELETE FROM collect WHERE pid = %s AND uid = %s
                    """,
                    (data["pid"],data["uid"]) )

        return json({
            "message": "刪除成功",
        }, status=201)

    except Exception as e:
        return json({"error": f"服務器錯誤: {str(e)}"}, status=500)
#收藏查詢
@app.post("/api/favorites/get")
async def get_favorites(request):
    try:
        data = request.json
        if not data:
            return json({"error": "請求體為空"}, status=400)

        required_fields = ["pid", "uid"]
        if not all(key in data for key in required_fields):
            return json({"error": "缺少必要欄位"}, status=400)

        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                # 查詢收藏狀態
                await cur.execute(
                    """
                    SELECT COUNT(*) FROM collect WHERE pid = %s AND uid = %s
                    """,
                    (data["pid"], data["uid"])
                )
                result = await cur.fetchone()
                is_favorited = result[0] > 0

        return json({"isFavorited": is_favorited}, status=200)

    except Exception as e:
        return json({"error": f"服務器錯誤: {str(e)}"}, status=500)
#評分新增
@app.post("/api/score/add")
async def score_add(request):
    try:
        data = request.json
        required_fields = ["pid", "uid", "score"]
        if not all(key in data for key in required_fields):
            return json({"error": "缺少必要欄位"}, status=400)

        pid = data["pid"]
        uid = data["uid"]
        score = data["score"]

        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                # 檢查是否已存在評分
                await cur.execute(
                    """
                    SELECT COUNT(*) FROM score WHERE pid = %s AND uid = %s
                    """,
                    (pid, uid)
                )
                result = await cur.fetchone()
                exists = result[0] > 0

                if exists:
                    # 更新評分
                    await cur.execute(
                        """
                        UPDATE score SET rate_sc = %s WHERE pid = %s AND uid = %s
                        """,
                        (score, pid, uid)
                    )
                    return json({"message": "評分更新成功"}, status=200)
                else:
                    # 新增評分
                    await cur.execute(
                        """
                        INSERT INTO score (pid, uid, rate_sc)
                        VALUES (%s, %s, %s)
                        """,
                        (pid, uid, score)
                    )
                    return json({"message": "評分成功"}, status=201)

    except Exception as e:
        return json({"error": f"服務器錯誤: {str(e)}"}, status=500)
#評分查詢
@app.post("/api/scores/get")
async def get_score(request):
    try:
        data = request.json
        if not data:
            return json({"error": "請求體為空"}, status=400)

        required_fields = ["pid", "uid"]
        if not all(key in data for key in required_fields):
            return json({"error": "缺少必要欄位"}, status=400)

        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                # 查詢評分
                await cur.execute(
                    """
                    SELECT rate_sc FROM score WHERE pid = %s AND uid = %s
                    """,
                    (data["pid"], data["uid"])
                )
                result = await cur.fetchone()
                score = result[0] if result else None

        return json({"score": score}, status=200)

    except Exception as e:
        return json({"error": f"服務器錯誤: {str(e)}"}, status=500)
    
#update avatar 

       
#post新增        
@app.post("/api/post/post/create")
async def post_add(request):
    try:
        data = request.json
        required_fields = ["title", "cid", "uid", "una", "content"]
        if not all(key in data for key in required_fields):
            return json({"error": "缺少必要欄位"}, status=400)

        latest_id = await get_latest_post_id(app.ctx.pool)
        next_id = f"P{latest_id + 1}"

        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO post (pid, title, cid, uid, una, content)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (next_id, data["title"], data["cid"], 
                     data["uid"], data["una"], data["content"])
                )

        return json({
            "message": "貼文發佈成功",
            "pid": next_id
        }, status=201)

    except Exception as e:
        return json({"error": f"服務器錯誤: {str(e)}"}, status=500)
    
#圖片新增
@app.post("/api/upload")
async def upload_file(request):
    try:
        # 检查请求中是否包含文件
        if not request.files or 'file' not in request.files:
            return json({"error": "没有找到文件"}, status=400)
        
        # 获取文件对象 - 这里根据实际情况调整处理方式
        file_data = request.files.get('file')
        
        # 调试信息
        print(f"文件数据类型: {type(file_data)}")
        print(f"文件数据内容: {file_data}")
        
        # 处理不同类型的文件数据
        if isinstance(file_data, list):
            # 如果是列表，获取第一个元素
            if not file_data:
                return json({"error": "文件列表为空"}, status=400)
            file = file_data[0]
            # 继续检查file的类型
            print(f"列表中第一个文件类型: {type(file)}")
        else:
            file = file_data
        
        # 直接从请求中获取文件名
        # 多种可能的方式获取文件名
        filename = None
        
        # 尝试从Content-Disposition头获取
        for key, value in request.headers.items():
            if key.lower() == 'content-disposition':
                parts = value.split(';')
                for part in parts:
                    if 'filename=' in part:
                        filename = part.split('=')[1].strip('"\'')
                        break
        
        # 如果头部没有文件名，尝试其他方法
        if not filename:
            if hasattr(file, 'name'):
                filename = file.name
            elif hasattr(file, 'filename'):
                filename = file.filename
            elif 'filename' in dir(file):
                filename = file.filename
            else:
                # 生成随机文件名
                filename = f"upload_{uuid.uuid4().hex}"
                # 尝试根据MIME类型确定扩展名
                content_type = request.headers.get('content-type', '')
                if 'image/jpeg' in content_type:
                    filename += '.jpg'
                elif 'image/png' in content_type:
                    filename += '.png'
                elif 'image/gif' in content_type:
                    filename += '.gif'
                else:
                    filename += '.bin'  # 默认二进制文件
        
        print(f"文件名: {filename}")
        
        # 获取文件内容
        file_content = None
        if hasattr(file, 'body'):
            file_content = file.body
        elif hasattr(file, 'read'):
            file_content = await file.read()
        elif isinstance(file, bytes):
            file_content = file
        elif isinstance(file, str):
            # 如果是base64编码的字符串
            if file.startswith('data:'):
                # 解析base64
                header, encoded = file.split(",", 1)
                file_content = base64.b64decode(encoded)
            else:
                return json({"error": "无法处理字符串类型的文件数据"}, status=400)
        else:
            return json({"error": f"无法处理的文件类型: {type(file)}"}, status=400)
        
        if not file_content:
            return json({"error": "无法获取文件内容"}, status=400)
        
        # 获取文件扩展名
        file_ext = filename.split('.')[-1].lower() if '.' in filename else None
        
        # 如果没有扩展名，通过MIME类型尝试确定
        if not file_ext:
            content_type = request.headers.get('content-type', '')
            if 'image/jpeg' in content_type:
                file_ext = 'jpg'
            elif 'image/png' in content_type:
                file_ext = 'png'
            elif 'image/gif' in content_type:
                file_ext = 'gif'
            else:
                file_ext = 'bin'  # 默认二进制文件
        
        # 限制文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if file_ext not in allowed_extensions:
            return json({"error": f"不支持的文件类型: {file_ext}"}, status=400)
        
        # 创建保存文件的目录
        upload_dir = os.path.join("static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # 返回文件的URL
        file_url = f"http://localhost:8000/static/uploads/{unique_filename}"
        
        return json({"location": file_url}, status=201)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"上传错误: {str(e)}")
        return json({"error": f"服务器错误: {str(e)}"}, status=500)
    
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
                    "SELECT uid, una, email, role,birthday,usex,reg_date FROM users WHERE uid = %s",
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
                user["reg_date"] = (
                    user["reg_date"].isoformat() if user["reg_date"] else None
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

@app.get("/api/userfavorites/<uid>")
async def get_userfavorite_post(request, uid):
    """獲取該使用者收藏社群貼文信息的 API"""
    try:
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    """
                    SELECT post.pid, post.title, post.content, post.comm_count,
                    post.crea_date, post.una, post.cid, post.uid
                    FROM collect 
                    JOIN post ON collect.pid = post.pid where collect.uid=%s
                    """,
                    (uid,)
                )
                favorite_posts= await cur.fetchall()

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
                    for post in favorite_posts
                ]

                return json({"favorite_posts": response}, status=200)
    except Exception as e:
        print(f"Error in get_user_posts: {str(e)}")
        return json({"error": str(e)}, status=400)


@app.get("/api/userpost/<uid>")
async def get_user_post(request, uid):
    """獲取所有社群貼文信息的 API"""
    try:
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    "SELECT pid, cid, uid, una,title,content,comm_count,crea_date FROM post where uid=%s",
                    (uid),
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
        print(f"Error in get_userpost_posts: {str(e)}")
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
    
@app.get("/api/ncomment/<nid>")
async def get_all_ncomment(request, nid):
    """獲取所有貼文留言信息的 API"""
    try:
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    "SELECT uid,una,comm_id,nid,title,content,crea_date FROM comments where nid=%s",
                    (nid,),
                ),
                comments = await cur.fetchall()


                # 處理每個留言的數據
                response = [
                    {
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
@app.get("/api/news/all")
async def get_all_news(request):
    """獲取所有新聞信息的 API"""
    try:
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    "SELECT newstitle , news_id, journ, newsclass,news_content ,suggest, score ,crea_date FROM news"
                )
                newsies = await cur.fetchall()

                if not newsies:
                    return json({"error": "沒有找到任何新聞"}, status=404)

                # 處理每個新聞的數據
                response = [
                    {
                        "newstitle": news["newstitle"],
                        "news_id": news["news_id"],
                        "journ": news["journ"],
                        "newsclass": news["newsclass"],
                        "news_content": news["news_content"],
                        "suggest": news["suggest"],
                        "score": news["score"],
                        "crea_date": (
                            news["crea_date"].isoformat() if news["crea_date"] else None
                        ),
                    }
                    for news in newsies
                ]

                return json({"newsies": response}, status=200)
    except Exception as e:
        print(f"Error in get_all_newsies: {str(e)}")
        return json({"error": str(e)}, status=400)
@app.get("/api/news/<nid>")
async def get_news_info(request, nid):
    """獲取新聞信息的 API"""
    try:
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    "SELECT newstitle , news_id, journ, newsclass, news_content, suggest, score, crea_date FROM news WHERE news_id=%s",
                    (nid,),
                )
                new = await cur.fetchone()

                if not new:
                    print(f"News ID {nid} 不存在")
                    return json({"error": "找尋不到該貼文"}, status=404)

                # 處理 datetime 轉換格式
                news = dict(new)
                news["crea_date"] = news["crea_date"].isoformat() if news["crea_date"] else None

                print(f"成功獲取新聞: {news}")  # 添加日志
                return json({"news": news}, status=200)
    except Exception as e:
        print(f"Error in get_news_info: {str(e)}")  # 打印错误日志
        return json({"error": str(e)}, status=400)

@app.put("/api/post/update/<pid>")
async def post_comment_update(request, pid):
    try:
        data = request.json
        required_fields = ["title", "content"]
        if not all(key in data for key in required_fields):
            return json({"error": "缺少必要欄位"}, status=400)

        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                # 先檢查貼文是否存在
                await cur.execute(
                    "SELECT COUNT(*) FROM post WHERE pid = %s",
                    (pid,)
                )
                result = await cur.fetchone()
                if result[0] == 0:
                    return json({"error": "找不到該貼文"}, status=404)

                # 更新貼文內容
                await cur.execute(
                    """
                    UPDATE post
                    SET title = %s, content = %s 
                    WHERE pid = %s
                    """,
                    (data["title"], data["content"], pid)
                )

        return json({"message": "貼文更新成功"}, status=200)

    except Exception as e:
        return json({"error": f"服務器錯誤: {str(e)}"}, status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)