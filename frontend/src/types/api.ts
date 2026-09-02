import type { Role } from "@/lib/auth";

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_at?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AdminStudent {
  id: number;
  user_id: number;
  first_name: string;
  last_name: string;
  email: string;
  current_level: number;
  placement_score: number;
}

export interface AdminTeacher {
  id: number;
  user_id: number;
  first_name: string;
  last_name: string;
  email: string;
}

export interface StudentProfile {
  id: number;
  user_id: number;
  first_name: string;
  last_name: string;
  email: string;
  current_level: number;
  placement_score: number;
}

export interface StudentCurrentLevel {
  student_id: number;
  current_level: number;
}

export interface StudentProgressItem {
  student_id: number;
  lesson_id: number;
  lesson_title: string;
  chapter_id: number;
  chapter_title: string;
  chapter_order: number;
  completed: boolean;
  score: number | null;
  attempts: number;
}

export interface UnlockedLesson {
  lesson_id: number;
  lesson_title: string;
  chapter_id: number;
  chapter_title: string;
  chapter_order: number;
  content: string;
  completed: boolean;
  score: number | null;
  attempts: number;
  quiz_id: number | null;
}

export interface AvailableQuizQuestion {
  question_id?: number | null;
  question: string;
  question_type: string;
  options: string[];
  explanation?: string | null;
}

export interface AvailableQuiz {
  quiz_id: number;
  lesson_id: number;
  lesson_title: string;
  chapter_id: number;
  chapter_title: string;
  chapter_order: number;
  title: string;
  questions: AvailableQuizQuestion[];
}

export interface CompletedQuiz {
  quiz_id: number;
  lesson_id: number;
  lesson_title: string;
  chapter_id: number;
  chapter_title: string;
  score: number | null;
  attempts: number;
}

export interface ValidationTestResult {
  student_id?: number;
  quiz_id: number;
  lesson_id: number;
  lesson_title: string;
  chapter_id: number;
  chapter_title: string;
  level: number;
  score: number | null;
  passed: boolean;
  attempts: number;
}

export interface TeacherStudentSummary {
  student_id: number;
  user_id: number;
  first_name: string;
  last_name: string;
  email: string;
  current_level: number;
  placement_score: number;
}

export interface TeacherProgressItem {
  student_id: number;
  lesson_id: number;
  lesson_title: string;
  chapter_id: number;
  chapter_title: string;
  chapter_order: number;
  completed: boolean;
  score: number | null;
  attempts: number;
}

export interface PlacementTestResult {
  student_id: number;
  user_id: number;
  first_name: string;
  last_name: string;
  email: string;
  placement_score: number;
  current_level: number;
  assigned_level: number;
}

export interface TeacherStatistics {
  total_students: number;
  average_placement_score: number;
  average_current_level: number;
  total_completed_lessons: number;
  completion_rate: number;
  validation_pass_rate: number;
}

export interface PdfIngestionResponse {
  source_document: string;
  chunk_count: number;
  vector_ids: number[];
}

export interface AiGenerationRequest {
  title: string;
  subject: string;
  level: number;
  course_id?: number | null;
  chapter_id?: number | null;
  lesson_id?: number | null;
  student_id?: number | null;
  instruction?: string;
  extra_context?: Record<string, unknown>;
  locale?: string;
}

export interface GeneratedArtifactResponse {
  artifact_type: "lesson" | "quiz" | "placement_test" | "validation_test";
  artifact_id: number | null;
  title: string;
  payload: Record<string, unknown>;
}

export interface QuizSubmissionRequest {
  answers: { question_id?: number | null; answer: string }[];
}

export interface QuizSubmissionResultDetail {
  question_id: number;
  correct: boolean;
  correct_answer?: string | null;
  explanation?: string | null;
}

export interface QuizSubmissionResult {
  quiz_id: number;
  lesson_id: number;
  score: number | null;
  total: number;
  correct: number;
  attempts: number;
  details: QuizSubmissionResultDetail[];
}

export interface FieldUserForm {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}

export interface StudentFormValues extends FieldUserForm {
  current_level: number;
  placement_score: number;
}

export type CurrentUserRole = Role;
