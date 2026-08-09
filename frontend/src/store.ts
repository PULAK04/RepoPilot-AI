import { configureStore, createSlice, PayloadAction } from '@reduxjs/toolkit'

const initialToken = localStorage.getItem('repopilot_token') || ''

const authSlice = createSlice({
  name: 'auth',
  initialState: { token: initialToken },
  reducers: {
    setToken(state, action: PayloadAction<string>) {
      state.token = action.payload
      localStorage.setItem('repopilot_token', action.payload)
    },
    logout(state) {
      state.token = ''
      localStorage.removeItem('repopilot_token')
    },
  },
})

export const { setToken, logout } = authSlice.actions
export const store = configureStore({ reducer: { auth: authSlice.reducer } })
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
