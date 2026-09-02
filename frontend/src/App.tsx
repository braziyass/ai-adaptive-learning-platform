import { Route, Routes } from "react-router-dom";

import { AppShell } from "@/components/layout/app-shell";
import { RequireAuth, RoleLanding } from "@/components/layout/require-auth";
import { AdminDashboardPage } from "@/pages/admin-dashboard-page";
import { LessonsPage } from "@/pages/lessons-page";
import { LoginPage } from "@/pages/login-page";
import { PlacementTestPage } from "@/pages/placement-test-page";
import { QuizPage } from "@/pages/quiz-page";
import { StatisticsPage } from "@/pages/statistics-page";
import { StudentDashboardPage } from "@/pages/student-dashboard-page";
import { TeacherDashboardPage } from "@/pages/teacher-dashboard-page";
import { ValidationTestPage } from "@/pages/validation-test-page";

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<RequireAuth />}>
        <Route element={<AppShell />}>
          <Route path="/" element={<RoleLanding />} />
          <Route path="/admin/dashboard" element={<AdminDashboardPage />} />
          <Route path="/admin/students" element={<AdminDashboardPage />} />
          <Route path="/admin/teachers" element={<AdminDashboardPage />} />
          <Route path="/teacher/dashboard" element={<TeacherDashboardPage />} />
          <Route path="/teacher/students" element={<TeacherDashboardPage />} />
          <Route path="/student/dashboard" element={<StudentDashboardPage />} />
          <Route path="/lessons" element={<LessonsPage />} />
          <Route path="/quiz" element={<QuizPage />} />
          <Route path="/placement-test" element={<PlacementTestPage />} />
          <Route path="/validation-test" element={<ValidationTestPage />} />
          <Route path="/statistics" element={<StatisticsPage />} />
        </Route>
      </Route>
    </Routes>
  );
}
