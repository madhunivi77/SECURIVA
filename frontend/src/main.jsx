import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

import './styles/global.css';
import App from './App.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Agent from './pages/Agent.jsx';
import Security from './pages/Security.jsx';
import ChatBox from './pages/ChatBox.jsx';
import Homepage from './pages/Homepage.jsx'
import LoginForm from './pages/LoginForm.jsx';
import VoiceTest from './pages/VoiceTest.jsx';

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <Homepage />
      },
      {
        path: '/agent',
        element: <Agent />
      },
      {
        path: '/security',
        element: <Security />
      },
      { 
        path: '/chat',
        element: <ChatBox />
      },
      {
        path: '/login',
        element: <LoginForm />
      },
      {
        path: '/voice',
        element: <VoiceTest />
      }
    ]
  },
  {
    path: '/dashboard',
    element: <Dashboard />,
  }
]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
