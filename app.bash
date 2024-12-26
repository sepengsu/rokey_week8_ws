#!/bin/bash

# 프로젝트 디렉토리로 이동
cd ./src/project/project/gui

# FastAPI 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level debug