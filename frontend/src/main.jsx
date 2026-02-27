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
import ProviderForm from './pages/ProviderForm.jsx';
import LoginForm from './pages/LoginForm.jsx';
import SignupForm from './pages/SignupForm.jsx';
import VoiceTest from './pages/VoiceTest.jsx';
import Pricing from "./pages/Pricing";
import AutomationGrid from './components/AutomationGrid.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import Industry from './pages/Industry.jsx';
import Support from "./pages/Support.jsx";
import About from "./pages/About.jsx";
import Contact from "./pages/Contact.jsx";
import FAQ from "./pages/FAQ.jsx";

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
        path: "pricing",
        element: <Pricing />,
      },
      {
        path: "/support",
        element: <Support />,
      },
      {
        path: "/about",
        element: <About />,
      },
      {
        path: "/contact",
        element: <Contact />,
      },
      {
        path: "/industries",
        element: <Industry />
      },
      {
        path: "/faq",
        element: <FAQ />
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
