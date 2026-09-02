import { Navigate, Outlet, useLocation } from "react-router-dom";

import { getAuthSession, getDashboardPath } from "@/lib/auth";

export function RequireAuth() {
  const location = useLocation();
  const session = getAuthSession();

  if (!session) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}

export function RoleLanding() {
  const session = getAuthSession();
  return <Navigate to={getDashboardPath(session?.role)} replace />;
}
