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
import ProviderForm from './pages/ProviderForm.jsx';
import LoginForm from './pages/LoginForm.jsx';
import SignupForm from './pages/SignupForm.jsx';
import VoiceTest from './pages/VoiceTest.jsx';
import Pricing from "./pages/Pricing";
import Industry from './pages/Industry.jsx';

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
        path: '/provider', // select a login provider
        element: <ProviderForm />
      },
      {
        path: '/login', // Local login
        element: <LoginForm />
      },
      {
        path: '/signup', // create a new account
        element: <SignupForm />
      },
      {
        path: '/voice',
        element: <VoiceTest />
      },
      {
        path: "/pricing",
        element: <Pricing />,
      },
      {
        path: "/industries",
        element: <Industry />
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
