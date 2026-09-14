import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { adminApi, aiApi, authApi, studentApi, teacherApi } from "@/lib/api";
import { createSessionFromTokens, getDashboardPath, getRefreshToken, saveAuthSession, clearAuthSession } from "@/lib/auth";
import type { AiGenerationRequest, LoginRequest, StudentFormValues } from "@/types/api";

export const queryKeys = {
  adminStudents: ["admin", "students"] as const,
  adminTeachers: ["admin", "teachers"] as const,
  adminCourses: ["admin", "courses"] as const,
  adminChapters: (courseId: number | null) => ["admin", "courses", courseId, "chapters"] as const,
  adminLessons: (chapterId: number | null) => ["admin", "chapters", chapterId, "lessons"] as const,
  adminCourseLessons: (courseId: number | null) => ["admin", "courses", courseId, "lessons"] as const,
  adminPlacementTest: ["admin", "placement-test"] as const,
  aiPdfIngestion: ["ai", "pdf-ingestion"] as const,
  aiGeneration: ["ai", "generation"] as const,
  studentProfile: ["student", "profile"] as const,
  studentCurrentLevel: ["student", "current-level"] as const,
  studentProgress: ["student", "progress"] as const,
  studentUnlockedLessons: ["student", "unlocked-lessons"] as const,
  studentAvailableQuizzes: ["student", "available-quizzes"] as const,
  studentCompletedQuizzes: ["student", "completed-quizzes"] as const,
  studentValidationResults: ["student", "validation-results"] as const,
  studentAvailableValidationTests: ["student", "available-validation-tests"] as const,
  studentPlacementTest: ["student", "placement-test"] as const,
  teacherStudents: ["teacher", "students"] as const,
  teacherStatistics: ["teacher", "statistics"] as const,
};

export function useLoginMutation() {
  return useMutation({
    mutationFn: (payload: LoginRequest) => authApi.login(payload),
    onSuccess: (tokens) => {
      saveAuthSession(createSessionFromTokens(tokens.access_token, tokens.refresh_token));
    },
  });
}

export function useLogoutMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const refreshToken = getRefreshToken();
      if (refreshToken) {
        await authApi.logout(refreshToken);
      }
    },
    onSettled: () => {
      clearAuthSession();
      queryClient.clear();
      window.location.assign("/login");
    },
  });
}

export function useAdminStudentsQuery() {
  return useQuery({ queryKey: queryKeys.adminStudents, queryFn: adminApi.listStudents });
}

export function useAdminTeachersQuery() {
  return useQuery({ queryKey: queryKeys.adminTeachers, queryFn: adminApi.listTeachers });
}

export function useAdminCoursesQuery() {
  return useQuery({ queryKey: queryKeys.adminCourses, queryFn: adminApi.listCourses });
}

export function useAdminChaptersQuery(courseId: number | null) {
  return useQuery({
    queryKey: queryKeys.adminChapters(courseId),
    queryFn: () => adminApi.listChapters(courseId as number),
    enabled: courseId !== null,
  });
}

export function useAdminLessonsQuery(chapterId: number | null) {
  return useQuery({
    queryKey: queryKeys.adminLessons(chapterId),
    queryFn: () => adminApi.listLessons(chapterId as number),
    enabled: chapterId !== null,
  });
}

export function useAdminCourseLessonsQuery(courseId: number | null) {
  return useQuery({
    queryKey: queryKeys.adminCourseLessons(courseId),
    queryFn: () => adminApi.listCourseLessons(courseId as number),
    enabled: courseId !== null,
  });
}

export function useAdminPlacementTestQuery() {
  return useQuery({
    queryKey: queryKeys.adminPlacementTest,
    queryFn: adminApi.getPlacementTest,
    retry: false,
  });
}

export function useUpdatePlacementTestMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminApi.updatePlacementTest,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.adminPlacementTest });
    },
  });
}

export function useStudentProfileQuery() {
  return useQuery({ queryKey: queryKeys.studentProfile, queryFn: studentApi.profile });
}

export function useStudentCurrentLevelQuery() {
  return useQuery({ queryKey: queryKeys.studentCurrentLevel, queryFn: studentApi.currentLevel });
}

export function useStudentProgressQuery() {
  return useQuery({ queryKey: queryKeys.studentProgress, queryFn: studentApi.progress });
}

export function useStudentUnlockedLessonsQuery() {
  return useQuery({ queryKey: queryKeys.studentUnlockedLessons, queryFn: studentApi.unlockedLessons });
}

export function useStudentAvailableQuizzesQuery() {
  return useQuery({ queryKey: queryKeys.studentAvailableQuizzes, queryFn: studentApi.availableQuizzes });
}

export function useStudentCompletedQuizzesQuery() {
  return useQuery({ queryKey: queryKeys.studentCompletedQuizzes, queryFn: studentApi.completedQuizzes });
}

export function useStudentValidationResultsQuery() {
  return useQuery({ queryKey: queryKeys.studentValidationResults, queryFn: studentApi.validationResults });
}

export function useStudentAvailableValidationTestsQuery() {
  return useQuery({ queryKey: queryKeys.studentAvailableValidationTests, queryFn: studentApi.availableValidationTests });
}

export function useSubmitValidationTestMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ quizId, payload }: { quizId: number; payload: Parameters<typeof studentApi.submitValidationTest>[1] }) =>
      studentApi.submitValidationTest(quizId, payload),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.studentProfile }),
        queryClient.invalidateQueries({ queryKey: queryKeys.studentCurrentLevel }),
        queryClient.invalidateQueries({ queryKey: queryKeys.studentAvailableValidationTests }),
        queryClient.invalidateQueries({ queryKey: queryKeys.studentValidationResults }),
        queryClient.invalidateQueries({ queryKey: queryKeys.studentUnlockedLessons }),
      ]);
    },
  });
}

export function useStudentPlacementTestQuery(enabled = true) {
  return useQuery({ queryKey: queryKeys.studentPlacementTest, queryFn: studentApi.placementTest, enabled });
}

export function useSubmitPlacementTestMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: studentApi.submitPlacementTest,
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.studentProfile }),
        queryClient.invalidateQueries({ queryKey: queryKeys.studentCurrentLevel }),
        queryClient.invalidateQueries({ queryKey: queryKeys.studentUnlockedLessons }),
      ]);
    },
  });
}

export function useTeacherStudentsQuery() {
  return useQuery({ queryKey: queryKeys.teacherStudents, queryFn: teacherApi.students });
}

export function useTeacherStatisticsQuery() {
  return useQuery({ queryKey: queryKeys.teacherStatistics, queryFn: teacherApi.statistics });
}

export function useCreateStudentMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminApi.createStudent,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.adminStudents });
    },
  });
}

export function useUpdateStudentMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, payload }: { studentId: number; payload: StudentFormValues }) => adminApi.updateStudent(studentId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.adminStudents });
    },
  });
}

export function useDeleteStudentMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminApi.deleteStudent,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.adminStudents });
    },
  });
}

export function useCreateTeacherMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminApi.createTeacher,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.adminTeachers });
    },
  });
}

export function useUpdateTeacherMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ teacherId, payload }: { teacherId: number; payload: Omit<StudentFormValues, "current_level" | "placement_score"> }) => adminApi.updateTeacher(teacherId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.adminTeachers });
    },
  });
}

export function useDeleteTeacherMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminApi.deleteTeacher,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.adminTeachers });
    },
  });
}

export function useUploadPdfMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: aiApi.uploadPdf,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.aiPdfIngestion });
    },
  });
}

export function useGenerateArtifactMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ artifactType, payload }: { artifactType: "lesson" | "quiz" | "placement_test" | "validation_test"; payload: AiGenerationRequest }) =>
      aiApi.generateArtifact(artifactType, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.aiGeneration });
    },
  });
}

export function useRoleSession() {
  return useQuery({
    queryKey: ["auth", "session"],
    queryFn: async () => null,
    initialData: null,
  });
}
