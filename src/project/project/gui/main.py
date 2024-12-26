from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import rclpy
import asyncio
import cv2
import numpy as np
from gui_node import GuiNode  # GuiNode가 구현된 파일에서 가져오기

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


# Mock user database
users = {"user@example.com": "password123"}  # 이메일과 비밀번호를 딕셔너리로 저장

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    """Handle login form submission."""
    if email in users and users[email] == password:
        # 로그인 성공
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="session", value=email)  # 세션 쿠키 설정
        return response
    else:
        # 로그인 실패
        request.session["error"] = "Invalid email or password"  # 에러 메시지 저장
        return RedirectResponse(url="/", status_code=302)
    
@app.on_event("startup")
async def startup_event():
    """FastAPI 시작 시 GuiNode 실행"""
    asyncio.create_task(run_ros2_node())


@app.on_event("shutdown")
async def shutdown_event():
    """FastAPI 종료 시 GuiNode 정리"""
    gui_node.destroy_node()
    rclpy.shutdown()


async def run_ros2_node():
    """ROS 2 노드를 비동기로 실행"""
    while rclpy.ok():
        rclpy.spin_once(gui_node, timeout_sec=0.1)
        await asyncio.sleep(0.1)


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

    # ROS 2 이미지 데이터 가져오기
    world_image = gui_node.world_camera_frame or np.zeros((480, 640, 3), dtype=np.uint8)  # 기본 검정 이미지
    robot_image = gui_node.robot_camera_frame or np.zeros((480, 640, 3), dtype=np.uint8)  # 기본 검정 이미지

    # Base64로 변환
    world_image_b64 = encode_image_to_base64(world_image)
    robot_image_b64 = encode_image_to_base64(robot_image)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": session,
            "world_image": world_image_b64,
            "robot_image": robot_image_b64,
        },
    )



@app.get("/logout")
async def logout(request: Request):
    """Handle user logout."""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("session")  # Clear the session cookie
    return response


def encode_image_to_base64(image):
    """Convert an image to Base64 for embedding in HTML."""
    try:
        if image is None:
            # 기본 검정 이미지 생성
            image = np.zeros((480, 640, 3), dtype=np.uint8)
        success, buffer = cv2.imencode('.jpg', image)
        if not success:
            raise ValueError("Failed to encode image to JPEG")
        return f"data:image/jpeg;base64,{buffer.tobytes().hex()}"
    except Exception as e:
        print(f"Error in encode_image_to_base64: {e}")
        # 에러 발생 시 기본 검정 이미지 반환
        default_image = np.zeros((480, 640, 3), dtype=np.uint8)
        _, buffer = cv2.imencode('.jpg', default_image)
        return f"data:image/jpeg;base64,{buffer.tobytes().hex()}"
