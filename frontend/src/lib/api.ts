import axios, { type AxiosError, type AxiosResponse, type InternalAxiosRequestConfig } from "axios";

import { clearAuthSession, createSessionFromTokens, getAccessToken, getRefreshToken, saveAuthSession } from "@/lib/auth";
import type {
  AiGenerationRequest,
  AdminChapter,
  AdminCourse,
  AdminLesson,
  AdminStudent,
  AdminTeacher,
  AuthTokens,
  AvailableQuiz,
  GeneratedArtifactResponse,
  LoginRequest,
  PdfIngestionResponse,
  PlacementTest,
  PlacementTestResult,
  PlacementTestSubmissionResult,
  StudentCurrentLevel,
  StudentFormValues,
  StudentProfile,
  StudentProgressItem,
  TeacherProgressItem,
  TeacherStatistics,
  TeacherStudentSummary,
  UnlockedLesson,
  ValidationTestResult,
  ValidationTestSubmissionResult,
  QuizSubmissionRequest,
  QuizSubmissionResult,
} from "@/types/api";

const API_URL = import.meta.env.VITE_API_URL ?? "/api/v1";

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    return null;
  }

  if (!refreshPromise) {
    refreshPromise = api
      .post<AuthTokens>("/auth/refresh", { refresh_token: refreshToken }, { skipAuthRefresh: true } as never)
      .then((response: AxiosResponse<AuthTokens>) => {
        const nextSession = createSessionFromTokens(response.data.access_token, response.data.refresh_token);
        saveAuthSession(nextSession);
        return nextSession.accessToken;
      })
      .catch(() => {
        clearAuthSession();
        return null;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }

  return refreshPromise;
}

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean; skipAuthRefresh?: boolean }) | undefined;
    if (!originalRequest || originalRequest.skipAuthRefresh || error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;
    const nextAccessToken = await refreshAccessToken();
    if (!nextAccessToken) {
      return Promise.reject(error);
    }

    originalRequest.headers = originalRequest.headers ?? {};
    originalRequest.headers.Authorization = `Bearer ${nextAccessToken}`;
    return api(originalRequest);
  },
);

export const authApi = {
  login(payload: LoginRequest) {
    return api.post<AuthTokens>("/auth/login", payload).then((response: AxiosResponse<AuthTokens>) => response.data);
  },
  logout(refreshToken: string) {
    return api.post("/auth/logout", { refresh_token: refreshToken }, { skipAuthRefresh: true } as never).then((response: AxiosResponse) => response.data);
  },
};

export const adminApi = {
  listStudents() {
    return api.get<AdminStudent[]>("/admin/students").then((response: AxiosResponse<AdminStudent[]>) => response.data);
  },
  createStudent(payload: StudentFormValues) {
    return api.post<AdminStudent>("/admin/students", payload).then((response: AxiosResponse<AdminStudent>) => response.data);
  },
  updateStudent(studentId: number, payload: StudentFormValues) {
    return api.put<AdminStudent>(`/admin/students/${studentId}`, payload).then((response: AxiosResponse<AdminStudent>) => response.data);
  },
  deleteStudent(studentId: number) {
    return api.delete<void>(`/admin/students/${studentId}`).then((response: AxiosResponse<void>) => response.data);
  },
  listTeachers() {
    return api.get<AdminTeacher[]>("/admin/teachers").then((response: AxiosResponse<AdminTeacher[]>) => response.data);
  },
  createTeacher(payload: Omit<StudentFormValues, "current_level" | "placement_score">) {
    return api.post<AdminTeacher>("/admin/teachers", payload).then((response: AxiosResponse<AdminTeacher>) => response.data);
  },
  updateTeacher(teacherId: number, payload: Omit<StudentFormValues, "current_level" | "placement_score">) {
    return api.put<AdminTeacher>(`/admin/teachers/${teacherId}`, payload).then((response: AxiosResponse<AdminTeacher>) => response.data);
  },
  deleteTeacher(teacherId: number) {
    return api.delete<void>(`/admin/teachers/${teacherId}`).then((response: AxiosResponse<void>) => response.data);
  },
  listCourses() {
    return api.get<AdminCourse[]>("/admin/courses").then((response: AxiosResponse<AdminCourse[]>) => response.data);
  },
  listChapters(courseId: number) {
    return api.get<AdminChapter[]>(`/admin/courses/${courseId}/chapters`).then((response: AxiosResponse<AdminChapter[]>) => response.data);
  },
  listLessons(chapterId: number) {
    return api.get<AdminLesson[]>(`/admin/chapters/${chapterId}/lessons`).then((response: AxiosResponse<AdminLesson[]>) => response.data);
  },
};

export const studentApi = {
  profile() {
    return api.get<StudentProfile>("/student/profile").then((response: AxiosResponse<StudentProfile>) => response.data);
  },
  currentLevel() {
    return api.get<StudentCurrentLevel>("/student/current-level").then((response: AxiosResponse<StudentCurrentLevel>) => response.data);
  },
  progress() {
    return api.get<StudentProgressItem[]>("/student/progress").then((response: AxiosResponse<StudentProgressItem[]>) => response.data);
  },
  unlockedLessons() {
    return api.get<UnlockedLesson[]>("/student/unlocked-lessons").then((response: AxiosResponse<UnlockedLesson[]>) => response.data);
  },
  availableQuizzes() {
    return api.get<AvailableQuiz[]>('/student/available-quizzes').then((response: AxiosResponse<AvailableQuiz[]>) => response.data);
  },
  submitQuiz(quizId: number, payload: QuizSubmissionRequest) {
    return api.post<QuizSubmissionResult>(`/student/quizzes/${quizId}/submit`, payload).then((response: AxiosResponse<QuizSubmissionResult>) => response.data);
  },
  completedQuizzes() {
    return api.get<unknown[]>("/student/completed-quizzes").then((response: AxiosResponse<unknown[]>) => response.data);
  },
  validationResults() {
    return api.get<ValidationTestResult[]>("/student/validation-results").then((response: AxiosResponse<ValidationTestResult[]>) => response.data);
  },
  availableValidationTests() {
    return api.get<AvailableQuiz[]>("/student/validation-tests").then((response: AxiosResponse<AvailableQuiz[]>) => response.data);
  },
  submitValidationTest(quizId: number, payload: QuizSubmissionRequest) {
    return api
      .post<ValidationTestSubmissionResult>(`/student/validation-tests/${quizId}/submit`, payload)
      .then((response: AxiosResponse<ValidationTestSubmissionResult>) => response.data);
  },
  placementTest() {
    return api.get<PlacementTest>("/student/placement-test").then((response: AxiosResponse<PlacementTest>) => response.data);
  },
  submitPlacementTest(payload: QuizSubmissionRequest) {
    return api
      .post<PlacementTestSubmissionResult>("/student/placement-test/submit", payload)
      .then((response: AxiosResponse<PlacementTestSubmissionResult>) => response.data);
  },
};

export const teacherApi = {
  students() {
    return api.get<TeacherStudentSummary[]>("/teacher/students").then((response: AxiosResponse<TeacherStudentSummary[]>) => response.data);
  },
  studentProgress(studentId: number) {
    return api.get<TeacherProgressItem[]>(`/teacher/students/${studentId}/progress`).then((response: AxiosResponse<TeacherProgressItem[]>) => response.data);
  },
  placementResult(studentId: number) {
    return api.get<PlacementTestResult>(`/teacher/students/${studentId}/placement-result`).then((response: AxiosResponse<PlacementTestResult>) => response.data);
  },
  validationResults(studentId: number) {
    return api.get<ValidationTestResult[]>(`/teacher/students/${studentId}/validation-results`).then((response: AxiosResponse<ValidationTestResult[]>) => response.data);
  },
  statistics() {
    return api.get<TeacherStatistics>("/teacher/statistics").then((response: AxiosResponse<TeacherStatistics>) => response.data);
  },
};

export const aiApi = {
  uploadPdf(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return api
      .post<PdfIngestionResponse>("/ai/pdfs/upload", formData, { headers: { "Content-Type": "multipart/form-data" } })
      .then((response: AxiosResponse<PdfIngestionResponse>) => response.data);
  },
  generateArtifact(artifactType: "lesson" | "quiz" | "placement_test" | "validation_test", payload: AiGenerationRequest) {
    return api
      .post<GeneratedArtifactResponse>(`/ai/generate/${artifactType}`, payload)
      .then((response: AxiosResponse<GeneratedArtifactResponse>) => response.data);
  },
};
