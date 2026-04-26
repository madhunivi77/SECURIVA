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
import UsersPage from "./pages/admin_pages/UsersPage";
import UserProfile from "./pages/admin_pages/UserProfile";
import AdminDashboard from './pages/admin_pages/AdminDashboard.jsx';
import AdminLayout from './pages/admin_pages/AdminLayout.jsx';
import AdminHandbook from './pages/admin_pages/AdminHandbook.jsx';
import AdminPayments from './pages/admin_pages/AdminPayments';
import AdminSecurity from './pages/admin_pages/AdminSecurity';
import AdminAnalytics from './pages/admin_pages/AdminAnalytics';
import AdminIntegrations from './pages/admin_pages/AdminIntegration';
import AdminContent from './pages/admin_pages/AdminCMS';
import AdminNotifications from './pages/admin_pages/AdminNotification';
import AdminActivity from './pages/admin_pages/AdminActivity';
import AdminSettings from './pages/admin_pages/AdminSettings';
import ToolsPage from './pages/ToolsPage.jsx';
import Firewall from './pages/Firewall.jsx';
import PrivacyPolicy from './pages/PrivacyPolicy.jsx';
import TermsOfService from './pages/TermsOfService.jsx';
import DataProcessingAgreement from './pages/DataProcessingAgreement.jsx';
import CookiePolicy from './pages/CookiePolicy.jsx';
import SecurityPolicy from './pages/SecurityPolicy.jsx';
import ComplianceOverview from './pages/ComplianceOverview.jsx';
import AIHandbook from './pages/AIHandbook.jsx';
import Billing from './pages/Billing.jsx';
import BillingManagement from './pages/BillingManagement.jsx';

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
        path: "/billing",
        element: <Billing />,
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
      }, 
      {
        path: "/privacy-policy",
        element: <PrivacyPolicy/>
      },
      {
        path: "/terms-of-service",
        element: <TermsOfService/>
      },
      {
        path: "/data-processing-agreement",
        element: <DataProcessingAgreement/>
      },
      {
        path: "/cookie-policy",
        element: <CookiePolicy/>
      },
      {
        path: "/security-policy",
        element: <SecurityPolicy/>
      },
      {
        path: "/compliance-overview",
        element: <ComplianceOverview/>
      }
    ]
  },
  {
    path: '/provider',
    element: <ProviderForm />
  },
  {
    path: '/login',
    element: <LoginForm />
  },
  {
    path: '/signup',
    element: <SignupForm />
  },
  {
    path: '/admin',
    element: <AdminLayout />,
    children: [
      {
        index: true,
        element: <AdminDashboard />
      },
      {
        path: "users",
        element: <UsersPage />,
      },
      {
        path: "users/:userId",
        element: <UserProfile />,
      },
      {
        path: "handbook",
        element: <AdminHandbook />,
      },
      {
        path: "security",
        element: <AdminSecurity />,
      },
      {
        path: "settings",
        element: <AdminSettings />,
      },
      {
        path: "notifications",
        element: <AdminNotifications />,
      },
      {
        path: "activity",
        element: <AdminActivity />,
      },
      {
        path: "integrations",
        element: <AdminIntegrations />,
      },
      {
        path: "payments",
        element: <AdminPayments />,
      },
      {
        path: "content",
        element: <AdminContent />,
      },
      {
        path: "analytics",
        element: <AdminAnalytics />,
      },
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
            path: 'handbook',
            element: <AIHandbook />,
          },
          {
            path: 'billing',
            element: <BillingManagement />,
          },
          {
            path: 'integrations',
            element: <Integrations />
          },
          {
            path: 'tools',
            element: <ToolsPage />
          },
          {
            path: 'firewall',
            element: <Firewall />
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
