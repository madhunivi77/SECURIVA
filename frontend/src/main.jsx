import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

import './styles/global.css';
import { AuthProvider } from './context/AuthContext.jsx';
import App from './App.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Agent from './pages/Agent.jsx';
import Security from './pages/Security.jsx';
import ChatBox from './pages/ChatBox.jsx';
import Homepage from './pages/Homepage.jsx'
import LoginForm from './pages/LoginForm.jsx';
import VoiceTest from './pages/VoiceTest.jsx';
import Pricing from "./pages/Pricing";
import AutomationGrid from './components/AutomationGrid.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';

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
        path: '/login',
        element: <LoginForm />
      },
      {
        path: "pricing",
        element: <Pricing />,
      }
    ]
  },
  {
    path: '/dashboard',
    element: <ProtectedRoute />,
    children: [
      {
        element: <Dashboard />,
        children: [
          {
            index: true,
            element: <AutomationGrid />,
          },
          {
            path: 'chat',
            element: <ChatBox />,
          },
          {
            path: 'voice',
            element: <VoiceTest />,
          }
        ]
      }
    ]
  }
]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </StrictMode>,
)
