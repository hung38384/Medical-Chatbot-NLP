class DialogueState:
    """Lớp đại diện cho một trạng thái hội thoại."""
    def __init__(self, name, handler, transitions=None):
        self.name = name
        self.handler = handler
        self.transitions = transitions or {}  # {event: next_state}
    
    def handle(self, dialogue_manager, user_input):
        """Xử lý đầu vào của người dùng trong trạng thái hiện tại."""
        return self.handler(dialogue_manager, user_input)
    
    def get_next_state(self, event):
        """Trả về trạng thái tiếp theo dựa trên sự kiện."""
        return self.transitions.get(event)
    
    def add_transition(self, event, next_state):
        """Thêm một chuyển đổi trạng thái mới."""
        self.transitions[event] = next_state


class DialogueFlow:
    """Lớp quản lý luồng hội thoại dựa trên các trạng thái."""
    def __init__(self, initial_state=None):
        self.states = {}  # {state_name: DialogueState}
        self.current_state_name = initial_state
    
    def add_state(self, state):
        """Thêm một trạng thái vào luồng hội thoại."""
        self.states[state.name] = state
        # Nếu đây là trạng thái đầu tiên, đặt làm trạng thái khởi tạo
        if not self.current_state_name:
            self.current_state_name = state.name
    
    def process(self, dialogue_manager, user_input):
        """Xử lý đầu vào người dùng dựa trên trạng thái hiện tại."""
        if self.current_state_name not in self.states:
            raise ValueError(f"Trạng thái không hợp lệ: {self.current_state_name}")
        
        current_state = self.states[self.current_state_name]
        result = current_state.handle(dialogue_manager, user_input)
        
        # Nếu kết quả là một tuple (response, event), xử lý chuyển đổi trạng thái
        if isinstance(result, tuple) and len(result) == 2:
            response, event = result
            next_state_name = current_state.get_next_state(event)
            if next_state_name:
                self.current_state_name = next_state_name
            return response
        
        # Nếu không có chuyển đổi trạng thái, chỉ trả về phản hồi
        return result
    
    def get_current_state(self):
        """Trả về trạng thái hiện tại."""
        return self.states.get(self.current_state_name)
    
    def reset(self, initial_state=None):
        """Đặt lại luồng hội thoại về trạng thái ban đầu."""
        if initial_state and initial_state in self.states:
            self.current_state_name = initial_state
        elif self.states:
            # Đặt lại về trạng thái đầu tiên được thêm vào
            self.current_state_name = next(iter(self.states))