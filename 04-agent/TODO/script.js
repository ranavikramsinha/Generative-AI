document.addEventListener('DOMContentLoaded', () => {
  const todoInput = document.getElementById('todo-input');
  const addBtn = document.getElementById('add-btn');
  const todoList = document.getElementById('todo-list');
  const darkModeToggle = document.getElementById('dark-mode-toggle');

  function createTodoItem(text) {
    const li = document.createElement('li');
    li.className = 'todo-item';

    const span = document.createElement('span');
    span.textContent = text;

    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Delete';
    deleteBtn.className = 'delete-btn';

    deleteBtn.addEventListener('click', () => {
      todoList.removeChild(li);
    });

    li.appendChild(span);
    li.appendChild(deleteBtn);
    return li;
  }

  addBtn.addEventListener('click', () => {
    const text = todoInput.value.trim();
    if (text !== '') {
      const todoItem = createTodoItem(text);
      todoList.appendChild(todoItem);
      todoInput.value = '';
      todoInput.focus();
    }
  });

  todoInput.addEventListener('keyup', (event) => {
    if(event.key === 'Enter') {
      addBtn.click();
    }
  });

  darkModeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    if(document.body.classList.contains('dark-mode')) {
      darkModeToggle.textContent = 'Light Mode';
    } else {
      darkModeToggle.textContent = 'Dark Mode';
    }
  });
});