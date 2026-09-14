import { Navigate, Outlet, useLocation } from "react-router-dom";

import { getAuthSession, getDashboardPath } from "@/lib/auth";
import { useStudentProfileQuery } from "@/lib/query-hooks";

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

const PLACEMENT_TEST_PATH = "/placement-test";

export function RequireStudentPlacement() {
  const session = getAuthSession();
  const location = useLocation();
  const profileQuery = useStudentProfileQuery();

  if (session?.role !== "student" || location.pathname === PLACEMENT_TEST_PATH) {
    return <Outlet />;
  }

  if (profileQuery.isLoading) {
    return null;
  }

  if (profileQuery.data && !profileQuery.data.placement_completed_at) {
    return <Navigate to={PLACEMENT_TEST_PATH} replace />;
  }

  return <Outlet />;
}
