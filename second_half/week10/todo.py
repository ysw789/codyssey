# 실행 방법 : python3 todo.py
# 테스트 명령어
#   - Todo 추가
#   curl -X POST http://localhost:8000/add_todo -H "Content-Type: application/json" -d '{"task": "과제하기", "description": "FastAPI 프로젝트"}'
#   - Todo 목록 조회
#   curl -X GET http://localhost:8000/retrieve_todo
#   - Todo 개별 조회
#   curl -X GET http://localhost:8000/get_single_todo/1
#   - Todo 수정
#   curl -X PUT http://localhost:8000/update_todo/1 -H "Content-Type: application/json" -d '{"id": 1, "task": "수정된 과제", "description": "수정된 설명"}'
#   - Todo 삭제
#   curl -X DELETE http://localhost:8000/delete_single_todo/1

from fastapi import FastAPI, APIRouter, HTTPException, Request
from typing import Dict, List
import uvicorn
import json
import csv
import os
from model import TodoItem, TodoResponse


CSV_FILE = 'todos.csv'
todo_list: List[Dict] = []


def load_todos() -> List[Dict]:
    """CSV 파일에서 todo 목록을 로드합니다."""
    if not os.path.exists(CSV_FILE):
        return []
    
    todos = []
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                todo = {
                    'id': int(row['id']),
                    'task': row['task'],
                    'description': row.get('description', '')
                }
                todos.append(todo)
    except (FileNotFoundError, ValueError, KeyError):
        return []
    
    return todos


def save_todos(todos: List[Dict]) -> None:
    """todo 목록을 CSV 파일에 저장합니다."""
    with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
        if not todos:
            writer = csv.writer(f)
            writer.writerow(['id', 'task', 'description'])
            return
        
        fieldnames = ['id', 'task', 'description']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for todo in todos:
            writer.writerow({
                'id': todo['id'],
                'task': todo['task'],
                'description': todo.get('description', '')
            })


def get_next_id() -> int:
    """다음 사용 가능한 ID를 반환합니다."""
    if not todo_list:
        return 1
    max_id = max(todo['id'] for todo in todo_list)
    return max_id + 1


# 시작 시 CSV에서 데이터 로드
todo_list = load_todos()


router = APIRouter()


"""
todo_list에 새로운 항목을 추가합니다.

Args:
    request: HTTP 요청 객체
    
Returns:
    추가된 todo 항목과 성공 메시지를 포함한 Dict
"""
@router.post('/add_todo', response_model=TodoResponse)
async def add_todo(request: Request) -> TodoResponse:
    try:
        body = await request.json()
        todo_item = body if isinstance(body, dict) else {}
    except (json.JSONDecodeError, ValueError):
        # 입력이 올바르지 않으면 HTTP 400 오류 응답
        raise HTTPException(status_code=400, detail='입력이 올바르지 않습니다.')
    
    new_id = get_next_id()
    new_todo = {
        'id': new_id,
        'task': todo_item.get('task', ''),
        'description': todo_item.get('description', '')
    }
    todo_list.append(new_todo)
    save_todos(todo_list)
    
    return TodoResponse(
        status='success',
        message='Todo 항목이 성공적으로 추가되었습니다.',
        data=new_todo
    )


"""
todo_list를 가져옵니다.

Returns:
    todo_list를 포함한 TodoResponse
"""
@router.get('/retrieve_todo', response_model=TodoResponse)
def retrieve_todo() -> TodoResponse:    
    return TodoResponse(
        status='success',
        data={
            'todos': todo_list,
            'count': len(todo_list)
        }
    )


"""
특정 ID의 todo 항목을 조회합니다.

Args:
    todo_id: 조회할 todo 항목의 ID
    
Returns:
    조회된 todo 항목을 포함한 Dict
"""
@router.get('/get_single_todo/{todo_id}', response_model=TodoResponse)
def get_single_todo(todo_id: int) -> TodoResponse:
    todo = next((t for t in todo_list if t['id'] == todo_id), None)
    if todo is None:
        raise HTTPException(status_code=404, detail='Todo 항목을 찾을 수 없습니다.')
    
    return TodoResponse(
        status='success',
        data=todo
    )


"""
특정 ID의 todo 항목을 수정합니다.

Args:
    todo_id: 수정할 todo 항목의 ID
    todo_item: 수정할 내용을 담은 TodoItem 모델
    
Returns:
    수정된 todo 항목과 성공 메시지를 포함한 Dict
"""
@router.put('/update_todo/{todo_id}', response_model=TodoResponse)
async def update_todo(todo_id: int, todo_item: TodoItem) -> TodoResponse:
    todo = next((t for t in todo_list if t['id'] == todo_id), None)
    if todo is None:
        raise HTTPException(status_code=404, detail='Todo 항목을 찾을 수 없습니다.')
    
    # 경로 매개변수의 id와 모델의 id가 일치하는지 확인
    if todo_item.id != todo_id:
        raise HTTPException(status_code=400, detail='경로 매개변수의 ID와 요청 본문의 ID가 일치하지 않습니다.')
    
    todo['task'] = todo_item.task
    todo['description'] = todo_item.description
    save_todos(todo_list)
    
    return TodoResponse(
        status='success',
        message='Todo 항목이 성공적으로 수정되었습니다.',
        data=todo
    )


"""
특정 ID의 todo 항목을 삭제합니다.

Args:
    todo_id: 삭제할 todo 항목의 ID
    
Returns:
    삭제 성공 메시지를 포함한 Dict
"""
@router.delete('/delete_single_todo/{todo_id}', response_model=TodoResponse)
def delete_single_todo(todo_id: int) -> TodoResponse:
    todo = next((t for t in todo_list if t['id'] == todo_id), None)
    if todo is None:
        raise HTTPException(status_code=404, detail='Todo 항목을 찾을 수 없습니다.')
    
    todo_list.remove(todo)
    save_todos(todo_list)
    
    return TodoResponse(
        status='success',
        message='Todo 항목이 성공적으로 삭제되었습니다.'
    )


app = FastAPI()
app.include_router(router)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
