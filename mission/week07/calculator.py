from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

class CalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('iPhone Calculator')
        self.setFixedSize(320, 550)
        self.setStyleSheet('background-color: black;')
        
        # 메인 위젯과 레이아웃 설정
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)
        
        # 계산기 결과 표시 영역을 화면 아래쪽으로 밀기 위한 스페이서
        self.spacer = QWidget()
        self.spacer.setSizePolicy(2, 0)  # 가로, 세로 (0 = 고정)
        self.layout.addWidget(self.spacer)
        
        # 계산 과정 표시 레이블
        self.expression_display = QLabel('')
        self.expression_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.expression_display.setStyleSheet('color: #999999; font-size: 30px; margin-bottom: 5px;')
        self.expression_display.setMinimumHeight(40)
        self.layout.addWidget(self.expression_display)
        
        # 결과 표시 레이블
        self.display = QLabel('0')
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setStyleSheet('color: white; font-size: 70px; margin-bottom: 20px;')
        self.display.setMinimumHeight(100)
        self.layout.addWidget(self.display)
        
        # 버튼 그리드 레이아웃
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)
        self.layout.addLayout(self.grid_layout)
        
        # 계산기 상태 변수들
        self.current_number = '0'
        self.stored_number = None
        self.operation = None
        self.reset_input = True
        self.last_button_was_equals = False
        self.expression = ''  # 계산 과정 누적 표시를 위한 변수
        self.complete_expression = ''  # 완전한 표현식을 저장하는 변수
        
        # 버튼 생성
        self.create_buttons()
        
    def create_buttons(self):
        # 버튼 데이터: 텍스트, 행, 열, 열 병합, 색상
        buttons = [
            ('AC', 0, 0, 1, 'gray'),
            ('±', 0, 1, 1, 'gray'),
            ('%', 0, 2, 1, 'gray'),
            ('÷', 0, 3, 1, 'orange'),
            ('7', 1, 0, 1, 'darkgray'),
            ('8', 1, 1, 1, 'darkgray'),
            ('9', 1, 2, 1, 'darkgray'),
            ('×', 1, 3, 1, 'orange'),
            ('4', 2, 0, 1, 'darkgray'),
            ('5', 2, 1, 1, 'darkgray'),
            ('6', 2, 2, 1, 'darkgray'),
            ('-', 2, 3, 1, 'orange'),
            ('1', 3, 0, 1, 'darkgray'),
            ('2', 3, 1, 1, 'darkgray'),
            ('3', 3, 2, 1, 'darkgray'),
            ('+', 3, 3, 1, 'orange'),
            ('0', 4, 0, 2, 'darkgray'),
            ('.', 4, 2, 1, 'darkgray'),
            ('=', 4, 3, 1, 'orange'),
        ]
        
        button_size = 70
        
        for button_text, row, col, colspan, color in buttons:
            button = QPushButton(button_text)
            
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
                if color == 'orange':
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
                elif color == 'gray':
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
                else:  # darkgray
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
        button = self.sender()
        button_text = button.text()
        
        if button_text in '0123456789':
            self.handle_number(button_text)
        elif button_text == '.':
            self.handle_decimal()
        elif button_text in '+-×÷':
            self.handle_operation(button_text)
        elif button_text == '=':
            self.calculate_result()
            self.last_button_was_equals = True
        elif button_text == 'AC':
            self.clear_all()
        elif button_text == '%':
            self.handle_percentage()
        elif button_text == '±':
            self.toggle_sign()
    
    def handle_number(self, number):
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
            if self.current_number == '0':
                self.current_number = number
            else:
                self.current_number += number
                
            # 화면 업데이트
            self.update_display()
            
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
                
        # 숫자가 너무 길면 입력 제한
        if len(self.current_number.replace('.', '').replace('-', '')) > 9:
            return
    
    def handle_decimal(self):
        # 등호 버튼 이후에는 새 계산 시작
        if self.last_button_was_equals:
            self.current_number = '0'
            self.last_button_was_equals = False
            self.complete_expression = ''
            self.expression_display.setText('')
            
        if self.reset_input:
            self.current_number = '0.'
            self.reset_input = False
            
            # 현재 입력 중인 숫자 추가 (연산자 다음)
            if self.operation:
                self.complete_expression = self.expression + ' 0.'
                self.expression_display.setText(self.complete_expression)
        elif '.' not in self.current_number:
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
        self.last_button_was_equals = False
        
        # 연산자 변경만 하는 경우
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
            
        # 연산이 이미 진행 중이면 먼저 결과 계산
        if self.stored_number is not None and not self.reset_input:
            self.calculate_result(update_expression=False)
            
        # 현재 숫자와 연산자 저장
        self.stored_number = float(self.current_number)
        self.operation = operation
        
        # 현재 숫자의 포맷팅된 버전 가져오기
        formatted_current = self.format_number(self.current_number)
        
        # 계산식 업데이트
        if not self.complete_expression:
            self.complete_expression = formatted_current + ' ' + operation
        elif self.complete_expression and self.complete_expression[-1] in '+-×÷':
            self.complete_expression = self.complete_expression[:-1] + operation
        else:
            self.complete_expression += ' ' + operation
            
        self.expression = self.complete_expression  # 표현식 상태 저장
        self.expression_display.setText(self.complete_expression)
        self.reset_input = True
    
    def calculate_result(self, update_expression=True):
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
            
            # 연산 수행
            if self.operation == '+':
                result = self.stored_number + current
            elif self.operation == '-':
                result = self.stored_number - current
            elif self.operation == '×':
                result = self.stored_number * current
            elif self.operation == '÷':
                if current == 0:
                    self.display.setText('Error')
                    self.expression_display.setText('Error')
                    self.reset_calculator_state()
                    return
                result = self.stored_number / current
            
            # 결과를 문자열로 변환하고 포맷팅
            result_str = str(result)
            # 정수 결과의 경우 소수점 이하 0 제거
            if result_str.endswith('.0'):
                result_str = result_str[:-2]
            
            self.current_number = result_str
            self.stored_number = None
            self.operation = None
            self.reset_input = True
            
            # 새 계산을 위한 표현식 초기화
            if update_expression:
                self.expression = ''
            else:
                # 중간 계산 결과는 새 표현식의 시작점이 됨
                self.expression = self.format_number(self.current_number)
                self.complete_expression = self.expression
                self.expression_display.setText(self.complete_expression)
            
            self.update_display()
    
    def handle_percentage(self):
        self.last_button_was_equals = False
        current = float(self.current_number)
        
        if self.stored_number is not None:
            # 저장된 숫자의 백분율 계산
            result = self.stored_number * (current / 100)
        else:
            # 현재 숫자를 백분율로 변환
            result = current / 100
            
        result_str = str(result)
        if result_str.endswith('.0'):
            result_str = result_str[:-2]
        
        self.current_number = result_str
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
        self.last_button_was_equals = False
        if self.current_number != '0':
            if self.current_number.startswith('-'):
                self.current_number = self.current_number[1:]
            else:
                self.current_number = '-' + self.current_number
            
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
        self.current_number = '0'
        self.stored_number = None
        self.operation = None
        self.reset_input = True
        self.last_button_was_equals = False
        self.expression = ''
        self.complete_expression = ''
        self.expression_display.setText('')
        self.update_display()
    
    def format_number(self, number_str):
        """숫자 문자열을 포맷팅하여 반환"""
        try:
            # 지수 표기법 처리
            if 'e' in number_str.lower():
                return number_str
                
            if '.' in number_str:
                integer_part, decimal_part = number_str.split('.')
                negative = integer_part.startswith('-')
                if negative:
                    integer_part = integer_part[1:]
                    
                if integer_part == '' or integer_part == '0':
                    formatted_integer = '0'
                else:
                    formatted_integer = f'{int(integer_part):,}'
                    
                if negative:
                    formatted_integer = '-' + formatted_integer
                    
                return f'{formatted_integer}.{decimal_part}'
            else:
                negative = number_str.startswith('-')
                if negative:
                    integer_part = number_str[1:]
                else:
                    integer_part = number_str
                    
                formatted_integer = f'{int(integer_part):,}'
                
                if negative:
                    formatted_integer = '-' + formatted_integer
                    
                return formatted_integer
        except ValueError:
            return number_str
    
    def update_display(self):
        formatted_number = self.format_number(self.current_number)
        
        # 숫자 길이에 따라 폰트 크기 조정
        if len(formatted_number) > 11:
            self.display.setStyleSheet('color: white; font-size: 40px; margin-bottom: 20px;')
        elif len(formatted_number) > 9:
            self.display.setStyleSheet('color: white; font-size: 50px; margin-bottom: 20px;')
        else:
            self.display.setStyleSheet('color: white; font-size: 70px; margin-bottom: 20px;')
            
        self.display.setText(formatted_number)
    
    def reset_calculator_state(self):
        self.current_number = '0'
        self.stored_number = None
        self.operation = None
        self.reset_input = True
        self.last_button_was_equals = False
        self.expression = ''
        self.complete_expression = ''

if __name__ == '__main__':
    app = QApplication([])  # sys.argv 대신 빈 리스트 사용
    calculator = CalculatorApp()
    calculator.show()
    app.exec_()  # sys.exit() 제거
