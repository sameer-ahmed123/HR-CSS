import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import type { UserRole } from "../types";

export default function ProtectedRoute({ roles }: { roles?: UserRole[] }) {
  const { isAuthenticated, loading, user } = useAuth();
  const location = useLocation();
  if (loading)
    return (
      <div className="grid min-h-screen place-items-center bg-ink text-mist">
        Loading workspace...
      </div>
    );
  if (!isAuthenticated)
    return <Navigate to="/login" replace state={{ from: location }} />;
  if (roles && user && !roles.includes(user.role))
    return <Navigate to="/403" replace />;
  return <Outlet />;
}
