import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

import './styles/global.css';
import { AuthProvider } from './context/AuthContext.jsx';
import { ThemeProvider } from './context/ThemeContext.jsx';
import App from './App.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Agent from './pages/Agent.jsx';
import Features from './pages/Features.jsx';
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
import Solutions from './pages/Solutions.jsx';
import Platform from './pages/Platform.jsx';
import AgentVoice from './pages/AgentVoice.jsx';
import AgentText from './pages/AgentText.jsx';
import Cybersecurity from './pages/Cybersecurity.jsx';
import VPN from './pages/VPN.jsx';
import Integrations from './pages/Integrations.jsx';
import Home from './pages/Home.jsx';
import Logs from './pages/Logs.jsx';

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
        path: '/solutions',
        element: <Solutions />
      },
      {
        path: '/features',
        element: <Features />
      },
      {
        path: "/pricing",
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
      },
      {
        path: "/platform",
        element: <Platform />
      },
      {
        path: "/agent-voice",
        element: <AgentVoice />
      },
      {
        path: "/agent-text",
        element: <AgentText />
      },
      {
        path: "/cybersecurity",
        element: <Cybersecurity />
      },
      {
        path: "/vpn",
        element: <VPN />
      }
    ]
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
    path: '/dashboard',
    element: <ProtectedRoute />,
    children: [
      {
        element: <Dashboard />,
        children: [
          {
            index: true,
            element: <Home />,
          },
          {
            path: 'chat',
            element: <ChatBox />,
          },
          {
            path: 'voice',
            element: <VoiceTest />,
          },
          {
            path: 'logs',
            element: <Logs />,
          },
          {
            path: 'integrations',
            element: <Integrations />,
          }
        ]
      }
    ]
  }
]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <ThemeProvider>
        <RouterProvider router={router} />
      </ThemeProvider>
    </AuthProvider>
  </StrictMode>,
)
