import threading
import base64
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import rclpy, cv2, asyncio, os, sys
import numpy as np
project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # 프로젝트 경로
sys.path.append(project_path)  # 프로젝트 경로를 파이썬 모듈 경로로 추가 
from project.gui.gui_node import GuiNode
from project.database import LoginDBHandler, DetectDBHandler
from fastapi.websockets import WebSocket

wait_time = 0.02  # 0.02초 대기
# FastAPI App Setup
app = FastAPI()

# Add Session Middleware
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# Static and Template Configuration
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ROS 2 노드 초기화
rclpy.init()
gui_node = GuiNode()  # GuiNode 인스턴스 생성

# 사용자 정보
db = LoginDBHandler() # LoginDBHandler 인스턴스 생성
users = db.get_users()  # 사용자 정보 가져오기
print(f"Users: {users}")
@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in users and users[username] == password:
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="session", value=username)
        return response
    else:
        request.session["error"] = "Invalid username or password"
        return RedirectResponse(url="/", status_code=302)

@app.on_event("startup")
async def startup_event():
    """FastAPI 시작 시 GuiNode 실행"""
    thread = threading.Thread(target=run_ros2_node, daemon=True)
    thread.start()

@app.on_event("shutdown")
async def shutdown_event():
    """FastAPI 종료 시 GuiNode 정리"""
    gui_node.destroy_node()
    rclpy.shutdown()

def run_ros2_node():
    """ROS 2 노드를 비동기로 실행"""
    while rclpy.ok():
        rclpy.spin_once(gui_node, timeout_sec=wait_time)

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render the login page."""
    error = request.session.pop("error", None)  # Retrieve and clear error message
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the dashboard page."""
    session = request.cookies.get("session")
    if not session:
        return RedirectResponse(url="/", status_code=302)

    try:
        # ROS 2 이미지 데이터 가져오기
        world_image = gui_node.world_camera_frame 
        robot_image = gui_node.robot_camera_frame  # np.ndarray 형식의 이미지 데이터
        print(type(world_image), type(robot_image))

        # Base64로 변환
        world_image_b64 = encode_image_to_base64(world_image)
        robot_image_b64 = encode_image_to_base64(robot_image)
    except Exception as e:
        print(f"Error fetching or encoding images: {e}")
        world_image_b64 = encode_image_to_base64(None)
        robot_image_b64 = encode_image_to_base64(None)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": session,
            "world_image": world_image_b64,
            "robot_image": robot_image_b64,
        },
    )

# 웹소켓 엔드포인트 --> 웹소켓을 통해 이미지 데이터 전송
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # ROS 2 이미지 데이터 가져오기
            world_image = gui_node.world_camera_frame
            robot_image = gui_node.robot_camera_frame

            # Base64로 변환
            world_image_b64 = encode_image_to_base64(world_image)
            robot_image_b64 = encode_image_to_base64(robot_image)

            # 클라이언트로 데이터 전송
            await websocket.send_json({
                "world_image": world_image_b64,
                "robot_image": robot_image_b64
            })

            # 0.1초 대기
            await asyncio.sleep(wait_time)
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        await websocket.close()

@app.get("/logout")
async def logout(request: Request):
    """Handle user logout."""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("session")  # Clear the session cookie
    return response

def encode_image_to_base64(image: np.ndarray):
    """Convert an image to Base64 for embedding in HTML."""
    try:
        if image is None or not isinstance(image, np.ndarray):
            image = np.zeros((480, 640, 3), dtype=np.uint8)
        success, buffer = cv2.imencode('.jpg', image) # np.ndarray를 JPEG로 인코딩
        if not success:
            raise ValueError("Failed to encode image to JPEG")
        encoded_image = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded_image}" # HTML img 태그에 넣을 수 있는 Base64 이미지 데이터 반환
    except Exception as e:
        print(f"Error in encode_image_to_base64: {e}")
        # Return black image in case of error
        default_image = np.zeros((480, 640, 3), dtype=np.uint8)
        _, buffer = cv2.imencode('.jpg', default_image)
        encoded_default_image = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded_default_image}"
