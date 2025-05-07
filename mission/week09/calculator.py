from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

class Calculator:
    """계산기의 계산 로직을 처리하는 클래스"""
    
    def __init__(self):
        """계산기 상태 초기화"""
        self.reset()
    
    def reset(self):
        """계산기 상태 초기화"""
        self.current_value = '0'
        self.stored_value = None
        self.operation = None
        self.reset_input = True
        return '0'
    
    def add(self, a, b):
        """두 숫자의 덧셈 수행"""
        return a + b
    
    def subtract(self, a, b):
        """두 숫자의 뺄셈 수행"""
        return a - b
    
    def multiply(self, a, b):
        """두 숫자의 곱셈 수행"""
        return a * b
    
    def divide(self, a, b):
        """두 숫자의 나눗셈 수행 (0으로 나누는 경우 처리)"""
        if b == 0:
            return "Error"
        return a / b
    
    def negative_positive(self, value):
        """숫자의 부호 전환"""
        if value == '0':
            return '0'  # 0은 부호 전환 불필요
        if value.startswith('-'):
            return value[1:]  # 음수 -> 양수
        return '-' + value  # 양수 -> 음수
    
    def percent(self, value, stored=None):
        """
        백분율 계산
        - stored가 None이면 현재 값의 1%를 계산
        - stored가 있으면 stored 값의 value% 계산
        """
        current = float(value)
        if stored is not None:
            return stored * (current / 100)  # 저장된 숫자의 percentage% 계산
        return current / 100  # 현재 숫자의 1% 계산
    
    def equal(self, a, b, operation):
        """현재 설정된 연산에 따라 계산 결과 반환"""
        if operation == '+':
            return self.add(a, b)
        elif operation == '-':
            return self.subtract(a, b)
        elif operation == '×':
            return self.multiply(a, b)
        elif operation == '÷':
            return self.divide(a, b)
        return b  # 연산이 없는 경우 현재 값 반환
    
    def format_result(self, result):
        """계산 결과를 포맷팅하여 문자열로 반환"""
        if isinstance(result, str):  # 이미 문자열(예: "Error")인 경우
            return result
        
        # 소수점 6자리 이하로 반올림 (보너스 요구사항)
        if isinstance(result, float):
            # 반올림
            rounded_result = round(result, 6)
            # 정수인 경우 소수점 제거
            if rounded_result == int(rounded_result):
                return str(int(rounded_result))
            return str(rounded_result)
        return str(result)


class CalculatorApp(QMainWindow):
    def __init__(self):
        """
        계산기 애플리케이션의 초기화 및 UI 구성
        """
        super().__init__()
        self.setWindowTitle('iPhone Calculator')  # 애플리케이션 창 제목 설정
        self.setFixedSize(320, 550)  # 창 크기 고정
        self.setStyleSheet('background-color: black;')  # 배경색 설정
        
        # 계산기 로직 클래스 인스턴스 생성
        self.calculator = Calculator()
        
        # 메인 위젯과 레이아웃 설정
        self.central_widget = QWidget()  # 메인 위젯 생성
        self.setCentralWidget(self.central_widget)  # 메인 위젯 설정
        self.layout = QVBoxLayout(self.central_widget)  # 세로 레이아웃 설정
        self.layout.setContentsMargins(10, 10, 10, 10)  # 레이아웃 여백 설정
        self.layout.setSpacing(5)  # 레이아웃 내부 간격 설정
        
        # 계산기 결과 표시 영역을 화면 아래쪽으로 밀기 위한 스페이서
        self.spacer = QWidget()
        self.spacer.setSizePolicy(2, 0)  # 가로, 세로 (0 = 고정)
        self.layout.addWidget(self.spacer)
        
        # 계산 과정 표시 레이블 - 상단에 현재 계산 과정 표시
        self.expression_display = QLabel('')
        self.expression_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # 오른쪽 정렬
        self.expression_display.setStyleSheet('color: #999999; font-size: 30px; margin-bottom: 5px;')
        self.expression_display.setMinimumHeight(40)
        self.layout.addWidget(self.expression_display)
        
        # 결과 표시 레이블 - 현재 입력된 숫자나 계산 결과 표시
        self.display = QLabel('0')
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # 오른쪽 정렬
        self.display.setStyleSheet('color: white; font-size: 70px; margin-bottom: 20px;')
        self.display.setMinimumHeight(100)
        self.layout.addWidget(self.display)
        
        # 버튼 그리드 레이아웃 - 계산기 버튼들 배치
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)  # 버튼 간 간격 설정
        self.layout.addLayout(self.grid_layout)
        
        # 계산기 상태 변수들 초기화
        self.current_number = '0'  # 현재 입력 중인 숫자
        self.stored_number = None  # 연산을 위해 저장된 이전 숫자
        self.operation = None  # 현재 선택된 연산자
        self.reset_input = True  # 새로운 숫자 입력 시작 여부
        self.last_button_was_equals = False  # 마지막 버튼이 등호였는지 여부
        self.expression = ''  # 계산 과정 누적 표시를 위한 변수
        self.complete_expression = ''  # 완전한 표현식을 저장하는 변수
        
        # 버튼 생성 및 배치
        self.create_buttons()
        
    def create_buttons(self):
        """
        계산기의 모든 버튼 생성 및 배치
        각 버튼에 스타일과 클릭 이벤트 핸들러 연결
        """
        # 버튼 데이터: 텍스트, 행, 열, 열 병합, 색상
        buttons = [
            ('AC', 0, 0, 1, 'gray'),    # 첫 번째 행 버튼들
            ('±', 0, 1, 1, 'gray'),
            ('%', 0, 2, 1, 'gray'),
            ('÷', 0, 3, 1, 'orange'),
            ('7', 1, 0, 1, 'darkgray'),  # 두 번째 행 버튼들
            ('8', 1, 1, 1, 'darkgray'),
            ('9', 1, 2, 1, 'darkgray'),
            ('×', 1, 3, 1, 'orange'),
            ('4', 2, 0, 1, 'darkgray'),  # 세 번째 행 버튼들
            ('5', 2, 1, 1, 'darkgray'),
            ('6', 2, 2, 1, 'darkgray'),
            ('-', 2, 3, 1, 'orange'),
            ('1', 3, 0, 1, 'darkgray'),  # 네 번째 행 버튼들
            ('2', 3, 1, 1, 'darkgray'),
            ('3', 3, 2, 1, 'darkgray'),
            ('+', 3, 3, 1, 'orange'),
            ('0', 4, 0, 2, 'darkgray'),  # 다섯 번째 행 버튼들 (0은 두 칸 차지)
            ('.', 4, 2, 1, 'darkgray'),
            ('=', 4, 3, 1, 'orange'),
        ]
        
        button_size = 70  # 버튼 크기 설정
        
        # 각 버튼 생성 및 설정
        for button_text, row, col, colspan, color in buttons:
            button = QPushButton(button_text)
            
            # 0 버튼은 길이가 두 배인 특수 버튼으로 처리
            if button_text == '0':
                button.setFixedSize(button_size*2 + 15, button_size)
                button.setStyleSheet(f'''
                    QPushButton {{
                        background-color: #333333;
                        color: white;
                        border-radius: {button_size//2}px;
                        font-size: 30px;
                        text-align: left;
                        padding-left: 28px;
                    }}
                    QPushButton:pressed {{
                        background-color: #606060;
                    }}
                ''')
            else:
                button.setFixedSize(button_size, button_size)
                
                # 색상에 따른 버튼 스타일 설정
                if color == 'orange':  # 연산자 버튼 스타일
                    button.setStyleSheet(f'''
                        QPushButton {{
                            background-color: #FF9500;
                            color: white;
                            border-radius: {button_size//2}px;
                            font-size: 30px;
                        }}
                        QPushButton:pressed {{
                            background-color: #FFB143;
                        }}
                    ''')
                elif color == 'gray':  # 상단 기능 버튼 스타일
                    button.setStyleSheet(f'''
                        QPushButton {{
                            background-color: #A5A5A5;
                            color: black;
                            border-radius: {button_size//2}px;
                            font-size: 30px;
                        }}
                        QPushButton:pressed {{
                            background-color: #D9D9D9;
                        }}
                    ''')
                else:  # 숫자 버튼 스타일
                    button.setStyleSheet(f'''
                        QPushButton {{
                            background-color: #333333;
                            color: white;
                            border-radius: {button_size//2}px;
                            font-size: 30px;
                        }}
                        QPushButton:pressed {{
                            background-color: #606060;
                        }}
                    ''')
            
            # 버튼 클릭 이벤트 연결
            button.clicked.connect(self.button_clicked)
            
            # 그리드에 버튼 추가
            self.grid_layout.addWidget(button, row, col, 1, colspan)
            
    def button_clicked(self):
        """
        버튼 클릭 이벤트 핸들러
        클릭된 버튼에 따라 적절한 동작 수행
        """
        button = self.sender()  # 클릭된 버튼 가져오기
        button_text = button.text()  # 버튼 텍스트 가져오기
        
        # 버튼 종류에 따라 적절한 메서드 호출
        if button_text in '0123456789':  # 숫자 버튼
            self.handle_number(button_text)
        elif button_text == '.':  # 소수점 버튼
            self.handle_decimal()
        elif button_text in '+-×÷':  # 연산자 버튼
            self.handle_operation(button_text)
        elif button_text == '=':  # 등호 버튼
            self.calculate_result()
            self.last_button_was_equals = True
        elif button_text == 'AC':  # 초기화 버튼
            self.clear_all()
        elif button_text == '%':  # 백분율 버튼
            self.handle_percentage()
        elif button_text == '±':  # 부호 전환 버튼
            self.toggle_sign()
    
    def handle_number(self, number):
        """
        숫자 버튼 클릭 시 처리
        현재 입력 상태에 따라 숫자 추가 또는 대체
        """
        # 등호 버튼 이후에는 새 계산 시작
        if self.last_button_was_equals:
            self.current_number = '0'
            self.last_button_was_equals = False
            self.reset_input = True
            self.complete_expression = ''
            self.expression_display.setText('')
            
        if self.reset_input:
            # 새 숫자 입력 시작 - 이전 숫자 대체
            self.current_number = number
            self.reset_input = False
            
            # 연산자 입력 후 첫 숫자가 표시되도록 함
            self.update_display()
            
            # 현재 입력 중인 숫자 추가 (연산자 다음)
            if self.operation:
                self.complete_expression = self.expression + ' ' + number
                self.expression_display.setText(self.complete_expression)
        else:
            # 현재 숫자에 입력된 숫자 추가
            if self.current_number == '0':  # 현재 숫자가 0이면 대체
                self.current_number = number
            else:  # 아니면 뒤에 추가
                self.current_number += number
                
            # 화면 업데이트
            self.update_display()
            
            # 현재 입력 중인 숫자 업데이트
            if self.operation:
                # 연산자 다음에 입력된 숫자를 업데이트
                last_space_index = self.complete_expression.rfind(' ')
                if last_space_index != -1:
                    self.complete_expression = self.complete_expression[:last_space_index+1] + self.current_number
                else:
                    self.complete_expression = self.current_number
            else:
                # 첫 번째 숫자 업데이트
                self.complete_expression = self.current_number
                
            self.expression_display.setText(self.complete_expression)
                
        # 숫자가 너무 길면 입력 제한 (9자리로 제한)
        if len(self.current_number.replace('.', '').replace('-', '')) > 9:
            return
    
    def handle_decimal(self):
        """
        소수점 버튼 클릭 시 처리
        현재 숫자에 소수점 추가
        """
        # 등호 버튼 이후에는 새 계산 시작
        if self.last_button_was_equals:
            self.current_number = '0'
            self.last_button_was_equals = False
            self.complete_expression = ''
            self.expression_display.setText('')
            
        if self.reset_input:
            # 새 숫자 입력 시작 - '0.'으로 시작
            self.current_number = '0.'
            self.reset_input = False
            
            # 현재 입력 중인 숫자 추가 (연산자 다음)
            if self.operation:
                self.complete_expression = self.expression + ' 0.'
                self.expression_display.setText(self.complete_expression)
        elif '.' not in self.current_number:
            # 현재 숫자에 소수점이 없을 경우에만 추가
            self.current_number += '.'
            
            # 현재 입력 중인 숫자 업데이트
            if self.operation:
                last_space_index = self.complete_expression.rfind(' ')
                if last_space_index != -1:
                    self.complete_expression = self.complete_expression[:last_space_index+1] + self.current_number
                else:
                    self.complete_expression = self.current_number
            else:
                self.complete_expression = self.current_number
                
            self.expression_display.setText(self.complete_expression)
        
        self.update_display()
    
    def handle_operation(self, operation):
        """
        연산자 버튼 클릭 시 처리
        현재 숫자와 연산자 저장 및 표현식 업데이트
        """
        self.last_button_was_equals = False
        
        # 연산자 변경만 하는 경우 (이미 연산자가 입력된 상태에서 다른 연산자 입력)
        if self.reset_input and self.operation:
            self.operation = operation
            # 마지막 연산자만 교체
            if self.complete_expression and self.complete_expression[-1] in '+-×÷':
                self.complete_expression = self.complete_expression[:-1] + operation
            elif self.complete_expression:
                self.complete_expression += ' ' + operation
            self.expression_display.setText(self.complete_expression)
            self.expression = self.complete_expression  # 최신 상태 저장
            return
            
        # 연산이 이미 진행 중이면 먼저 결과 계산 (연속 계산 처리)
        if self.stored_number is not None and not self.reset_input:
            self.calculate_result(update_expression=False)
            
        # 현재 숫자와 연산자 저장
        self.stored_number = float(self.current_number)
        self.operation = operation
        
        # 현재 숫자의 포맷팅된 버전 가져오기
        formatted_current = self.format_number(self.current_number)
        
        # 계산식 업데이트
        if not self.complete_expression:
            # 첫 번째 숫자와 연산자 추가
            self.complete_expression = formatted_current + ' ' + operation
        elif self.complete_expression and self.complete_expression[-1] in '+-×÷':
            # 이미 연산자가 있으면 마지막 연산자 교체
            self.complete_expression = self.complete_expression[:-1] + operation
        else:
            # 숫자 다음에 연산자 추가
            self.complete_expression += ' ' + operation
            
        self.expression = self.complete_expression  # 표현식 상태 저장
        self.expression_display.setText(self.complete_expression)
        self.reset_input = True  # 다음 숫자 입력을 위해 입력 상태 리셋
    
    def calculate_result(self, update_expression=True):
        """
        계산 수행 및 결과 표시
        저장된 숫자와 현재 숫자를 사용하여 연산 수행
        """
        if self.stored_number is not None and self.operation is not None:
            current = float(self.current_number)
            
            # 계산식에 현재 숫자 추가 (등호 버튼을 눌렀을 때만)
            if update_expression:
                formatted_current = self.format_number(self.current_number)
                last_space_index = self.complete_expression.rfind(' ')
                
                if last_space_index != -1 and last_space_index < len(self.complete_expression) - 1:
                    if self.complete_expression[last_space_index+1] in '+-×÷':
                        # 마지막이 연산자인 경우 숫자 추가
                        self.complete_expression += ' ' + formatted_current
                    else:
                        # 마지막 숫자 업데이트
                        self.complete_expression = self.complete_expression[:last_space_index+1] + formatted_current
                
                self.complete_expression += ' = '
                self.expression_display.setText(self.complete_expression)
            
            # Calculator 클래스를 사용하여 계산 수행
            result = self.calculator.equal(self.stored_number, current, self.operation)
            
            # 계산 결과를 문자열로 변환하고 포맷팅
            if result == "Error":
                self.display.setText('Error')
                self.expression_display.setText('Error')
                self.reset_calculator_state()
                return
                
            # 결과 포맷팅
            result_str = self.calculator.format_result(result)
            
            self.current_number = result_str
            self.stored_number = None
            self.operation = None
            self.reset_input = True
            
            # 새 계산을 위한 표현식 초기화
            if update_expression:
                self.expression = ''  # 등호 버튼 누른 경우 표현식 초기화
            else:
                # 중간 계산 결과는 새 표현식의 시작점이 됨
                self.expression = self.format_number(self.current_number)
                self.complete_expression = self.expression
                self.expression_display.setText(self.complete_expression)
            
            self.update_display()
    
    def handle_percentage(self):
        """
        백분율 버튼 클릭 시 처리
        현재 숫자를 백분율로 변환 (÷100)
        """
        self.last_button_was_equals = False
        
        # Calculator 클래스를 사용하여 백분율 계산
        if self.stored_number is not None:
            result = self.calculator.percent(self.current_number, self.stored_number)
        else:
            result = self.calculator.percent(self.current_number)
            
        # 결과 포맷팅
        result_str = self.calculator.format_result(result)
        self.current_number = result_str
        
        # 표현식 업데이트를 위한 포맷팅
        formatted_current = self.format_number(self.current_number)
        
        # 표현식 업데이트
        if not self.operation:
            self.complete_expression = formatted_current
        else:
            # 마지막 숫자를 백분율 결과로 업데이트
            last_space_index = self.complete_expression.rfind(' ')
            if last_space_index != -1 and last_space_index < len(self.complete_expression) - 1:
                if self.complete_expression[last_space_index+1] in '+-×÷':
                    # 마지막이 연산자인 경우 새 숫자 추가
                    self.complete_expression += ' ' + formatted_current
                else:
                    # 마지막 숫자 업데이트
                    self.complete_expression = self.complete_expression[:last_space_index+1] + formatted_current
            else:
                self.complete_expression = formatted_current
                
        self.expression_display.setText(self.complete_expression)
        self.update_display()
    
    def toggle_sign(self):
        """
        부호 전환 버튼 클릭 시 처리
        현재 숫자의 부호를 양수/음수로 전환
        """
        self.last_button_was_equals = False
        
        # Calculator 클래스의 negative_positive 메소드 사용
        self.current_number = self.calculator.negative_positive(self.current_number)
        
        # 부호 변경을 표현식에 반영
        formatted_current = self.format_number(self.current_number)
        
        if not self.operation:
            self.complete_expression = formatted_current
        else:
            # 마지막 숫자의 부호 변경
            last_space_index = self.complete_expression.rfind(' ')
            if last_space_index != -1 and last_space_index < len(self.complete_expression) - 1:
                if self.complete_expression[last_space_index+1] in '+-×÷':
                    # 마지막이 연산자인 경우 새 숫자 추가
                    self.complete_expression += ' ' + formatted_current
                else:
                    # 마지막 숫자 업데이트
                    self.complete_expression = self.complete_expression[:last_space_index+1] + formatted_current
            else:
                self.complete_expression = formatted_current
                
        self.expression_display.setText(self.complete_expression)
        self.update_display()
    
    def clear_all(self):
        """
        AC 버튼 클릭 시 처리
        모든 상태 및 표시 초기화
        """
        # Calculator 클래스의 reset 메소드 사용
        self.current_number = self.calculator.reset()
        self.stored_number = None
        self.operation = None
        self.reset_input = True
        self.last_button_was_equals = False
        self.expression = ''
        self.complete_expression = ''
        self.expression_display.setText('')
        self.update_display()
    
    def format_number(self, number_str):
        """
        숫자 문자열을 포맷팅하여 반환
        천 단위 구분 기호(,) 추가, 소수점 처리, 음수 처리 등
        """
        try:
            # 지수 표기법 처리 (예: 1e+10)
            if 'e' in number_str.lower():
                return number_str
                
            if '.' in number_str:  # 소수점이 있는 경우
                integer_part, decimal_part = number_str.split('.')
                negative = integer_part.startswith('-')
                if negative:
                    integer_part = integer_part[1:]  # 음수 부호 제거
                    
                # 정수 부분 포맷팅
                if integer_part == '' or integer_part == '0':
                    formatted_integer = '0'
                else:
                    formatted_integer = f'{int(integer_part):,}'  # 천 단위 구분 기호 추가
                    
                if negative:
                    formatted_integer = '-' + formatted_integer  # 음수 부호 다시 추가
                    
                return f'{formatted_integer}.{decimal_part}'
            else:  # 정수인 경우
                negative = number_str.startswith('-')
                if negative:
                    integer_part = number_str[1:]
                else:
                    integer_part = number_str
                    
                formatted_integer = f'{int(integer_part):,}'  # 천 단위 구분 기호 추가
                
                if negative:
                    formatted_integer = '-' + formatted_integer  # 음수 부호 추가
                    
                return formatted_integer
        except ValueError:
            # 숫자 포맷팅 중 오류 발생 시 원본 반환
            return number_str
    
    def update_display(self):
        """
        메인 디스플레이 업데이트 및 폰트 크기 자동 조정
        """
        formatted_number = self.format_number(self.current_number)
        
        # 숫자 길이에 따라 폰트 크기 조정 (보너스 요구사항)
        if len(formatted_number) > 11:
            # 11자리 초과: 작은 폰트
            self.display.setStyleSheet('color: white; font-size: 40px; margin-bottom: 20px;')
        elif len(formatted_number) > 9:
            # 9자리 초과: 중간 폰트
            self.display.setStyleSheet('color: white; font-size: 50px; margin-bottom: 20px;')
        else:
            # 9자리 이하: 큰 폰트
            self.display.setStyleSheet('color: white; font-size: 70px; margin-bottom: 20px;')
            
        self.display.setText(formatted_number)  # 화면에 숫자 표시
    
    def reset_calculator_state(self):
        """
        계산기 상태 완전 초기화 (오류 발생 등의 경우에 사용)
        """
        self.calculator.reset()
        self.current_number = '0'
        self.stored_number = None
        self.operation = None
        self.reset_input = True
        self.last_button_was_equals = False
        self.expression = ''
        self.complete_expression = ''

if __name__ == '__main__':
    app = QApplication([])  # PyQt 애플리케이션 초기화
    calculator = CalculatorApp()  # 계산기 인스턴스 생성
    calculator.show()  # 계산기 화면 표시
    app.exec_()  # 이벤트 루프 실행 (프로그램이 사용자 입력을 기다림)
