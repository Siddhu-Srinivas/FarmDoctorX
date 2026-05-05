import React, { createContext, useReducer, useContext } from 'react';

const ChatStateContext = createContext();
const ChatDispatchContext = createContext();

const initialState = {
  history: [] // { user: '', ai: {} }
};

function chatReducer(state, action) {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return {
        ...state,
        history: [...state.history, action.payload]
      };
    case 'CLEAR_HISTORY':
      return {
        ...state,
        history: []
      };
    default:
      throw new Error(`Unknown action: ${action.type}`);
  }
}

export function ChatProvider({ children }) {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  return (
    <ChatDispatchContext.Provider value={dispatch}>
      <ChatStateContext.Provider value={state}>
        {children}
      </ChatStateContext.Provider>
    </ChatDispatchContext.Provider>
  );
}

export function useChatState() {
  const context = useContext(ChatStateContext);
  if (context === undefined) {
    throw new Error('useChatState must be used within a ChatProvider');
  }
  return context;
}

export function useChatDispatch() {
  const context = useContext(ChatDispatchContext);
  if (context === undefined) {
    throw new Error('useChatDispatch must be used within a ChatProvider');
  }
  return context;
}
