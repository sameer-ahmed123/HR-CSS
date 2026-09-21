import { BrowserRouter, Route, Routes } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import { AuthProvider } from "./context/AuthContext";
import DashboardPage from "./pages/DashboardPage";
import ForbiddenPage from "./pages/ForbiddenPage";
import LoginPage from "./pages/auth/LoginPage";
import RegisterPage from "./pages/auth/RegisterPage";
import AcceptInvitePage from "./pages/auth/AcceptInvitePage";
import ProtectedRoute from "./routes/ProtectedRoute";
import ProfilePage from "./pages/ProfilePage";
import ForgotPasswordPage from "./pages/auth/ForgotPasswordPage";
import ResetPasswordPage from "./pages/auth/ResetPasswordPage";
import NotFoundPage from "./pages/NotFoundPage";
import PeoplePage from "./pages/PeoplePage";
import AccessControlPage from "./pages/AccessControlPage";
import RecruitmentOverviewPage from "./pages/RecruitmentOverviewPage";
import HiringRequestsPage from "./pages/HiringRequestsPage";
import HiringRequestReviewPage from "./pages/HiringRequestReviewPage";
import JobPostingsPage from "./pages/JobPostingsPage";
import JobPostingDetailPage from "./pages/JobPostingDetailPage";
import CareersPage from "./pages/CareersPage";
import CareerDetailPage from "./pages/CareerDetailPage";
import ApplyJobPage from "./pages/ApplyJobPage";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/accept-invite" element={<AcceptInvitePage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/403" element={<ForbiddenPage />} />
          <Route path="/careers" element={<CareersPage />} />
          <Route path="/careers/:jobId" element={<CareerDetailPage />} />
          <Route path="/careers/:jobId/apply" element={<ApplyJobPage />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route index element={<DashboardPage />} />
              <Route path="home" element={<DashboardPage />} />
              <Route path="profile" element={<ProfilePage />} />
              <Route path="people" element={<PeoplePage />} />
              <Route element={<ProtectedRoute roles={["ADMIN", "HR"]} />}>
                <Route path="access-control" element={<AccessControlPage />} />
              </Route>
              <Route
                element={
                  <ProtectedRoute roles={["ADMIN", "HR", "TEAM_LEAD"]} />
                }
              >
                <Route
                  path="recruitment"
                  element={<RecruitmentOverviewPage />}
                />
                <Route path="recruitment/jobs" element={<JobPostingsPage />} />
                <Route
                  path="recruitment/jobs/:jobId"
                  element={<JobPostingDetailPage />}
                />
                <Route
                  path="recruitment/jobs/:jobId/applications/:applicationId"
                  element={<JobPostingDetailPage />}
                />
              </Route>
              <Route element={<ProtectedRoute roles={["TEAM_LEAD"]} />}>
                <Route
                  path="recruitment/requests"
                  element={<HiringRequestsPage />}
                />
              </Route>
              <Route element={<ProtectedRoute roles={["ADMIN", "HR"]} />}>
                <Route
                  path="recruitment/review"
                  element={<HiringRequestReviewPage />}
                />
              </Route>
              <Route path="organization" element={<DashboardPage />} />
            </Route>
          </Route>
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
