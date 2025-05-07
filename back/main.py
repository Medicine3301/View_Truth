import json as jsonlib  # Rename json import to avoid conflict
import logging
from sanic import Sanic
from sanic.response import json  # This json is for responses
from sanic_cors import CORS
import aiomysql
import jwt
import bcrypt
import uuid
from datetime import datetime, timedelta
import sys
import os
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from json.decoder import JSONDecodeError
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#郵件認證的函式導入
from back.mail import EmailVerifier
from back.run_spider import run_spider
from back.geminisuccess import run_verification_system



app = Sanic("auth_app")
CORS(app)
#token配置
SECRET_KEY = "therealeyecanseethetruth"
JWT_ALGORITHM = "HS256" 
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # 訪問令牌過期時間
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # 刷新令牌過期時間
#db資訊
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456",
    "db": "new_community",
    "charset": "utf8mb4",
    "port": 3306
}

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 初始化調度器
scheduler = AsyncIOScheduler()

async def execute_spider():
    """執行爬蟲任務"""
    try:
        logger.info("開始執行爬蟲任務...")
        run_spider()
        logger.info("爬蟲任務完成")
        return True
    except Exception as e:
        logger.error(f"爬蟲任務執行失敗: {str(e)}")
        return False

async def execute_analysis():
    """執行新聞分析任務"""
    try:
        logger.info("開始執行新聞分析...")
        # 使用模組級別的函數而不是實例方法
        run_verification_system()
    except Exception as e:
        logger.error(f"新聞分析執行失敗: {str(e)}")
        return False

async def update_database():
    """更新資料庫任務"""
    try:
        logger.info("開始更新資料庫...")
        
        # 讀取 JSON 文件
        json_path = os.path.join(os.path.dirname(__file__), 'news_assessments.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = jsonlib.load(f)
            
        if not data.get('assessments'):
            logger.warning("沒有找到需要更新的評估數據")
            return False
            
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                for assessment in data['assessments']:
                    # 檢查記錄是否已存在
                    await cur.execute(
                        "SELECT nid FROM content_analysis WHERE link = %s",
                        (assessment['link'],)
                    )
                    exists = await cur.fetchone()
                    
                    if exists:
                        # 更新現有記錄
                        await cur.execute(
                            """
                            UPDATE content_analysis SET
                                title = %s,
                                img = %s,
                                content = %s,
                                publish_date = %s,
                                location = %s,
                                event_type = %s,
                                credibility_score = %s,
                                credibility_level = %s,
                                factual_score = %s,
                                critical_score = %s,
                                balanced_score = %s,
                                source_score = %s,
                                factual_analysis = %s,
                                critical_analysis = %s,
                                balanced_analysis = %s,
                                source_analysis = %s,
                                verification_guide = %s,
                                analysis_timestamp = %s
                            WHERE link = %s
                            """,
                            (
                                assessment['title'],
                                assessment['img'],
                                assessment['content'],
                                assessment['publish_date'],
                                assessment['location'],
                                assessment['event_type'],
                                assessment['credibility_score'],
                                assessment['credibility_level'],
                                assessment['factual_score'],
                                assessment['critical_score'],
                                assessment['balanced_score'],
                                assessment['source_score'],
                                jsonlib.dumps(assessment['factual_analysis']),
                                jsonlib.dumps(assessment['critical_analysis']),
                                jsonlib.dumps(assessment['balanced_analysis']),
                                jsonlib.dumps(assessment['source_analysis']),
                                jsonlib.dumps(assessment['verification_guide']),
                                assessment['analysis_timestamp'],
                                assessment['link']
                            )
                        )
                    else:
                        # 插入新記錄
                        await cur.execute(
                            """
                            INSERT INTO content_analysis (
                                link, img, title, content, publish_date, location,
                                event_type, credibility_score, credibility_level,
                                factual_score, critical_score, balanced_score,
                                source_score, factual_analysis, critical_analysis,
                                balanced_analysis, source_analysis, verification_guide,
                                analysis_timestamp
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s
                            )
                            """,
                            (
                                assessment['link'],
                                assessment['img'],
                                assessment['title'],
                                assessment['content'],
                                assessment['publish_date'],
                                assessment['location'],
                                assessment['event_type'],
                                assessment['credibility_score'],
                                assessment['credibility_level'],
                                assessment['factual_score'],
                                assessment['critical_score'],
                                assessment['balanced_score'],
                                assessment['source_score'],
                                jsonlib.dumps(assessment['factual_analysis']),
                                jsonlib.dumps(assessment['critical_analysis']),
                                jsonlib.dumps(assessment['balanced_analysis']),
                                jsonlib.dumps(assessment['source_analysis']),
                                jsonlib.dumps(assessment['verification_guide']),
                                assessment['analysis_timestamp']
                            )
                        )
                
        logger.info(f"成功更新 {len(data['assessments'])} 條新聞評估數據")
        return True
        
    except FileNotFoundError:
        logger.error("找不到 news_assessments.json 文件")
        return False
    except jsonlib.JSONDecodeError:
        logger.error("JSON 文件解析錯誤")
        return False
    except Exception as e:
        logger.error(f"資料庫更新失敗: {str(e)}")
        return False

@app.listener("before_server_start")
async def setup_services(app, loop):
    """初始化所有服務"""
    try:
        # 初始化資料庫連接池
        app.ctx.pool = await aiomysql.create_pool(
            **DB_CONFIG, 
            loop=loop, 
            autocommit=True,
            maxsize=15
        )
        logger.info("資料庫連接池已建立")

        # 初始化調度器
        scheduler.add_job(
            update_database,
            'cron',
            hour=18,
            minute=33,
            id='database_job'
        )
        
        # 添加任務監聽器，用於在一個任務完成後觸發下一個任務
        def job_listener(event):
            if event.exception:
                logger.error(f"任務執行出錯: {event.exception}")
            else:
                if event.job_id == 'spider_job':
                    # 爬蟲完成後，等待1分鐘再執行分析
                    scheduler.add_job(
                        execute_analysis,
                        'date',
                        run_date=datetime.now() + timedelta(seconds=5),
                        id='analysis_job'
                    )
                    logger.info("爬蟲任務完成，已排程分析任務")
                elif event.job_id == 'analysis_job':
                    # 分析完成後，等待1分鐘再執行資料庫更新
                    scheduler.add_job(
                        update_database,
                        'date',
                        run_date=datetime.now() + timedelta(seconds=5),
                        id='database_job'
                    )
                    logger.info("分析任務完成，已排程資料庫更新任務")
                elif event.job_id == 'database_job':
                    logger.info("資料庫更新任務完成")

        scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        scheduler.start()
        logger.info("調度器已啟動")

    except Exception as e:
        logger.error(f"服務初始化出錯: {str(e)}")
        raise

@app.listener('after_server_stop')
async def cleanup_services(app, loop):
    """清理所有服務"""
    try:
        scheduler.shutdown()
        logger.info("調度器已關閉")
        
        app.ctx.pool.close()
        await app.ctx.pool.wait_closed()
        logger.info("資料庫連接池已關閉")

    except Exception as e:
        logger.error(f"服務清理時出錯: {str(e)}")

# 任務狀態查詢API
@app.get("/api/tasks/status")
async def get_tasks_status(request):
    """獲取所有任務的狀態"""
    try:
        spider_job = scheduler.get_job('spider_job')
        analysis_job = scheduler.get_job('analysis_job')
        database_job = scheduler.get_job('database_job')
        
        return json({
            "spider_job": {
                "status": "scheduled" if spider_job else "not_scheduled",
                "next_run": spider_job.next_run_time.isoformat() if spider_job else None
            },
            "analysis_job": {
                "status": "scheduled" if analysis_job else "not_scheduled",
                "next_run": analysis_job.next_run_time.isoformat() if analysis_job else None
            },
            "database_job": {
                "status": "scheduled" if database_job else "not_scheduled",
                "next_run": database_job.next_run_time.isoformat() if database_job else None
            }
        })
    except Exception as e:
        logger.error(f"獲取任務狀態時出錯: {str(e)}")
        return json({"error": str(e)}, status=500)
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
        if (existing_user):
            return json({"error": "用戶名已存在"}, status=400)

        uid = str(uuid.uuid4())
        hashed_password = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())
        birthday_date = datetime.fromisoformat(data["birthday"]).date()

        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                # 插入用戶資料表
                await cur.execute(
                    """
                    INSERT INTO users (uid, una, birthday, usex, email, passwd)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (uid, data["name"], birthday_date, data["sex"], 
                     data["email"], hashed_password.decode())
                )
                # 註冊成功後，插入用戶統計數據表
                await cur.execute(
                    """
                    INSERT INTO user_statistics (uid, una) values (%s, %s)

                    """,
                    (uid, data["name"])
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
        required_fields = ["pid", "uid", "una", "content", "parent_id"]
        if not all(key in data for key in required_fields):
            return json({"error": "缺少必要欄位"}, status=400)

        latest_id = await get_latest_comm_id(app.ctx.pool)
        next_id = f"RP{latest_id + 1}"

        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO comments (pid, comm_id, uid, una, content, parent_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (data["pid"], next_id, data["uid"], data["una"], 
                     data["content"], data["parent_id"])
                )

        return json({
            "message": "留言成功",
            "comm_id": next_id
        }, status=201)

    except Exception as e:
        return json({"error": f"服務器錯誤: {str(e)}"}, status=500)

# 修改貼文評論的獲取API以支援巢狀結構
@app.get("/api/comment/<pid>")
async def get_all_comment(request, pid):
    """獲取所有貼文留言信息的 API"""
    try:
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    """
                    SELECT uid, una, comm_id, pid, content, crea_date, parent_id 
                    FROM comments 
                    WHERE pid = %s 
                    ORDER BY parent_id ASC, crea_date ASC
                    """,
                    (pid,)
                )
                comments = await cur.fetchall()
                
                # Convert datetime objects to ISO format strings
                for comment in comments:
                    if comment['crea_date']:
                        comment['crea_date'] = comment['crea_date'].isoformat()

                # Process the rest of the function...
                comment_dict = {}
                root_comments = []

                for comment in comments:
                    comment['children'] = []
                    comment_dict[comment['comm_id']] = comment
                    
                    if not comment['parent_id']:
                        root_comments.append(comment)
                    else:
                        parent = comment_dict.get(comment['parent_id'])
                        if parent:
                            parent['children'].append(comment)

                return json({"comments": root_comments}, status=200)
    except Exception as e:
        print(f"Error in get_all_comments: {str(e)}")
        return json({"error": str(e)}, status=400)

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
    

    
# 登入路由
@app.post("/api/login")
async def login(request):
    try:
        data = request.json
        user = await get_user_by_username(app.ctx.pool, data["username"])

        if not user:
            return json({"error": "用戶不存在"}, status=404)

        if not bcrypt.checkpw(data["password"].encode(), user["passwd"].encode()):
            return json({"error": "密碼錯誤"}, status=401)

        # 生成訪問令牌和刷新令牌
        access_token = jwt.encode(
            {
                "uid": user["uid"],
                "type": "access",
                "exp": datetime.utcnow() + JWT_ACCESS_TOKEN_EXPIRES
            },
            SECRET_KEY,
            algorithm=JWT_ALGORITHM
        )

        refresh_token = jwt.encode(
            {
                "uid": user["uid"], 
                "type": "refresh",
                "exp": datetime.utcnow() + JWT_REFRESH_TOKEN_EXPIRES
            },
            SECRET_KEY,
            algorithm=JWT_ALGORITHM
        )

        return json({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "uid": user["uid"],
                "una": user["una"], 
                "email": user["email"],
                "role": user["role"]
            }
        })

    except Exception as e:
        return json({"error": str(e)}, status=400)

# 新增刷新token的端點
@app.post("/api/refresh")
async def refresh_token(request):
    try:
        refresh_token = request.headers.get("Authorization", "").replace("Bearer ", "")
        
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            if payload["type"] != "refresh":
                return json({"error": "Invalid token type"}, status=400)
                
            # 生成新的訪問令牌
            access_token = jwt.encode(
                {
                    "uid": payload["uid"],
                    "type": "access", 
                    "exp": datetime.utcnow() + JWT_ACCESS_TOKEN_EXPIRES
                },
                SECRET_KEY,
                algorithm=JWT_ALGORITHM
            )
            
            return json({"access_token": access_token})
            
        except jwt.ExpiredSignatureError:
            return json({"error": "Refresh token expired"}, status=401)
        except jwt.InvalidTokenError:
            return json({"error": "Invalid refresh token"}, status=401)
            
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
                    """
                    SELECT pid, cid, uid, una, title, content, comm_count, 
                           crea_date, rate_sc, favorite 
                    FROM post 
                    WHERE cid = %s
                    """,
                    (cid,)
                )
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
                        "rate_sc": float(post["rate_sc"]) if post["rate_sc"] else 0,
                        "favorite": int(post["favorite"]) if post["favorite"] else 0,
                        "crea_date": post["crea_date"].isoformat() if post["crea_date"] else None,
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

    
@app.get("/api/ncomment/<nid>")
async def get_all_ncomment(request, nid):
    """獲取所有新聞留言信息的 API"""
    try:
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    """
                    SELECT uid, una, comm_id, nid, content, crea_date, parent_id 
                    FROM comments 
                    WHERE nid = %s 
                    ORDER BY parent_id ASC, crea_date ASC
                    """,
                    (nid,)
                )
                comments = await cur.fetchall()
                
                # Convert datetime objects to ISO format strings
                for comment in comments:
                    if comment['crea_date']:
                        comment['crea_date'] = comment['crea_date'].isoformat()

                # 處理巢狀結構
                comment_dict = {}
                root_comments = []

                for comment in comments:
                    comment['children'] = []
                    comment_dict[comment['comm_id']] = comment
                    
                    if not comment['parent_id']:
                        root_comments.append(comment)
                    else:
                        parent = comment_dict.get(comment['parent_id'])
                        if parent:
                            parent['children'].append(comment)

                return json({"comments": root_comments}, status=200)
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
                    """
                    SELECT nid, title, content, link,img, publish_date, location, 
                           event_type, credibility_score, credibility_level,
                           factual_score, critical_score, balanced_score, 
                           source_score, analysis_timestamp
                    FROM content_analysis
                    """
                )
                newsies = await cur.fetchall()

                if not newsies:
                    return json({"error": "沒有找到任何新聞"}, status=404)

                # 處理每個新聞的數據
                response = [
                    {
                        "nid": news["nid"],
                        "title": news["title"],
                        "content": news["content"],
                        "link": news["link"],
                        "img": news["img"],
                        "publish_date": news["publish_date"],
                        "location": news["location"],
                        "event_type": news["event_type"],
                        "credibility_score": float(news["credibility_score"]) if news["credibility_score"] else 0,
                        "credibility_level": news["credibility_level"],
                        "factual_score": float(news["factual_score"]) if news["factual_score"] else 0,
                        "critical_score": float(news["critical_score"]) if news["critical_score"] else 0,
                        "balanced_score": float(news["balanced_score"]) if news["balanced_score"] else 0,
                        "source_score": float(news["source_score"]) if news["source_score"] else 0,
                        "analysis_timestamp": news["analysis_timestamp"].isoformat() if news["analysis_timestamp"] else None,
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
                    """
                    SELECT nid, title, content, link,img, publish_date, location,
                           event_type, credibility_score, credibility_level,
                           factual_score, critical_score, balanced_score,
                           source_score, factual_analysis, critical_analysis,
                           balanced_analysis, source_analysis, verification_guide,
                           analysis_timestamp
                    FROM content_analysis 
                    WHERE nid = %s
                    """,
                    (nid,),
                )
                news = await cur.fetchone()

                if not news:
                    print(f"News ID {nid} 不存在")
                    return json({"error": "找尋不到該新聞"}, status=404)

                # 處理JSON字段
                json_fields = ['factual_analysis', 'critical_analysis', 
                             'balanced_analysis', 'source_analysis', 
                             'verification_guide']
                for field in json_fields:
                    if news[field]:
                        news[field] = jsonlib.loads(news[field])

                # 處理數值字段
                number_fields = ['credibility_score', 'factual_score', 
                               'critical_score', 'balanced_score', 'source_score']
                for field in number_fields:
                    if news[field]:
                        news[field] = float(news[field])

                # 處理時間戳
                if news["analysis_timestamp"]:
                    news["analysis_timestamp"] = news["analysis_timestamp"].isoformat()

                print(f"成功獲取新聞: {news}")
                return json({"news": news}, status=200)
    except Exception as e:
        print(f"Error in get_news_info: {str(e)}")
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
#user 統計數據獲取
@app.get("/api/users/statistics")
async def get_statistics_overview(request):
    try:
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                # 總用戶數
                await cur.execute("SELECT COUNT(*) AS totalUsers FROM users;")
                total_users = (await cur.fetchone())["totalUsers"]

                # 本月新增用戶數
                await cur.execute("""SELECT COUNT(*) AS monthlyNewUsers FROM users WHERE reg_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01');""")
                monthly_new_users = (await cur.fetchone())["monthlyNewUsers"]

                # 待處理檢舉數
                await cur.execute("""SELECT COUNT(*) AS pendingReports FROM reports WHERE status = 'pending';""")
                pending_reports = (await cur.fetchone())["pendingReports"]

                # 今日活躍用戶數
                await cur.execute("""SELECT COUNT(DISTINCT uid) AS todayActiveUsers FROM user_activity WHERE activity_time >= CURDATE();""")
                today_active_users = (await cur.fetchone())["todayActiveUsers"]

            return json({
                "totalUsers": total_users,
                "monthlyNewUsers": monthly_new_users,
                "pendingReports": pending_reports,
                "todayActiveUsers": today_active_users
            })
    except Exception as e:
        return json({"服務器錯誤": str(e)}, status=500)
#特定用戶獲取
@app.get("/api/user_statistics/<uid>")
async def get_user_statistics(request, uid):
    try:
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                # 查詢用戶基本信息
                await cur.execute(
                    "SELECT una, email, role, reg_date FROM users WHERE uid=%s",
                    (uid,),
                )
                user = await cur.fetchone()
                if not user:
                    print(f"UID {uid} 不存在")
                    return json({"error": "找尋不到該用戶"}, status=404)

                # 查詢用戶統計信息
                await cur.execute(
                    "SELECT status FROM user_statistics WHERE uid = %s",
                    (uid,),
                )
                status = await cur.fetchone()
                if not status:
                    return json({"error": "找不到該用戶統計信息"}, status=404)

                # 合併結果
                user_statistics = {
                    "una": user["una"],
                    "email": user["email"],
                    "role": user["role"],
                    "reg_date": user["reg_date"].isoformat() if user["reg_date"] else None,
                    "status": status["status"],
                }

                print(f"成功獲取用戶統計信息: {user_statistics}")  # 添加日志
                return json({"userdetail": user_statistics}, status=200)

    except Exception as e:
        return json({"服務器錯誤": str(e)}, status=500)
@app.get("/api/users")
async def get_users(request):
    """獲取用戶列表，支持篩選、分頁和排序，並包含其他表的 status 狀態"""
    try:
        # 獲取查詢參數
        una= request.args.get("una")  # 篩選條件：用戶名
        status = request.args.get("status")  # 篩選條件：用戶狀態
        start_date = request.args.get("start_date")  # 註冊開始日期
        end_date = request.args.get("end_date")  # 註冊結束日期
        page = int(request.args.get("page", 1))  # 分頁：當前頁數，默認第 1 頁
        page_size = int(request.args.get("pageSize", 10))  # 分頁：每頁大小，默認 10 條
        sort_by = request.args.get("sortBy", "reg_date")  # 排序字段，默認按註冊日期
        order = request.args.get("order", "desc")  # 排序順序，默認降序

        # 計算偏移量
        offset = (page - 1) * page_size

        # 構建 SQL 查詢
        query = """
            SELECT 
                users.uid, 
                users.una, 
                users.email, 
                users.role,
                users.reg_date, 
                user_statistics.status 
            FROM 
                users
            LEFT JOIN 
                user_statistics 
            ON 
                users.uid = user_statistics.uid
            WHERE 1=1
        """
        params = []

        # 添加篩選條件
        if una:
            query += " AND users.una LIKE %s"
            params.append(f"%{una}%")
        # 注意：這裡的 status 是用戶統計表中的狀態
        if status:
            query += " AND user_statistics.status = %s"
            params.append(status)
        if start_date:
            query += " AND users.reg_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND users.reg_date <= %s"
            params.append(end_date)

        # 添加排序條件
        if sort_by not in ["reg_date", "una"]:
            sort_by = "reg_date"  # 默認排序字段
        if order not in ["asc", "desc"]:
            order = "desc"  # 默認排序順序
        query += f" ORDER BY {sort_by} {order}"

        # 添加分頁條件
        query += " LIMIT %s OFFSET %s"
        params.extend([page_size, offset])

        # 執行查詢
        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, params)
                users = await cur.fetchall()

                # 處理 datetime 對象
                for user in users:
                    if user["reg_date"]:
                        user["reg_date"] = user["reg_date"].isoformat()

                # 查詢總記錄數
                count_query = """
                    SELECT COUNT(*) AS total 
                    FROM users
                    LEFT JOIN user_statistics 
                    ON users.uid = user_statistics.uid
                    WHERE 1=1
                """
                if una:
                    count_query += " AND users.una LIKE %s"
                if status:
                    count_query += " AND user_statistics.status = %s"
                if start_date:
                    count_query += " AND users.reg_date >= %s"
                if end_date:
                    count_query += " AND users.reg_date <= %s"

                await cur.execute(count_query, params[:-2])  # 不包括 LIMIT 和 OFFSET 的參數
                total = (await cur.fetchone())["total"]

        # 返回結果
        return json({"users": users, "total": total, "page": page, "pageSize": page_size}, status=200)

    except Exception as e:
        return json({"error": f"服務器錯誤: {str(e)}"}, status=500)

# 單個用戶封禁/解封
@app.put("/api/user/status")
async def update_user_status(request):
    try:
        data = request.json
        required_fields = ["uid", "status"]
        if not all(key in data for key in required_fields):
            return json({"error": "缺少必要欄位"}, status=400)

        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    UPDATE user_statistics 
                    SET status = %s 
                    WHERE uid = %s
                    """,
                    (data["status"], data["uid"])
                )

        return json({
            "message": "用戶狀態更新成功",
            "status": data["status"]
        }, status=200)

    except Exception as e:
        return json({"error": f"服務器錯誤: {str(e)}"}, status=500)

# 批量封禁
@app.put("/api/users/batch-status")
async def batch_update_user_status(request):
    try:
        data = request.json
        if not data.get("uids") or not data.get("status"):
            return json({"error": "缺少必要欄位"}, status=400)

        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                for uid in data["uids"]:
                    await cur.execute(
                        """
                        UPDATE user_statistics 
                        SET status = %s 
                        WHERE uid = %s
                        """,
                        (data["status"], uid)
                    )

        return json({
            "message": "批量更新用戶狀態成功",
            "affected": len(data["uids"])
        }, status=200)

    except Exception as e:
        return json({"error": f"服務器錯誤: {str(e)}"}, status=500)

@app.post("/api/news/comment/create")
async def news_comment_add(request):
    try:
        data = request.json
        required_fields = ["nid", "uid", "una", "content", "parent_id"]
        if not all(key in data for key in required_fields):
            return json({"error": "缺少必要欄位"}, status=400)

        latest_id = await get_latest_ncomm_id(app.ctx.pool)
        next_id = f"RN{latest_id + 1}"

        async with app.ctx.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO comments (nid, comm_id, uid, una, content, parent_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (data["nid"], next_id, data["uid"], data["una"], 
                     data["content"], data["parent_id"])
                )

        return json({
            "message": "留言成功",
            "comm_id": next_id
        }, status=201)

    except Exception as e:
        return json({"error": f"服務器錯誤: {str(e)}"}, status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)