import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/common/page-header";
import { useStudentAvailableQuizzesQuery, useStudentCompletedQuizzesQuery } from "@/lib/query-hooks";
import { useState } from "react";
import { studentApi } from "@/lib/api";
import type { QuizSubmissionRequest, QuizSubmissionResult } from "@/types/api";

export function QuizPage() {
  const availableQuizzesQuery = useStudentAvailableQuizzesQuery();
  const quizzesQuery = useStudentCompletedQuizzesQuery();
  const [answers, setAnswers] = useState<Record<number, Record<number | string, string>>>({});
  const [results, setResults] = useState<Record<number, QuizSubmissionResult | null>>({});

  const handleOptionChange = (quizId: number, questionId: number | string, value: string) => {
    setAnswers((prev) => ({ ...prev, [quizId]: { ...(prev[quizId] ?? {}), [questionId]: value } }));
  };

  const submitQuiz = async (quizId: number) => {
    const byQuestion = answers[quizId] ?? {};
    const payload: QuizSubmissionRequest = { answers: Object.entries(byQuestion).map(([qid, val]) => ({ question_id: Number(qid), answer: val })) };
    try {
      const res = await studentApi.submitQuiz(quizId, payload);
      setResults((prev) => ({ ...prev, [quizId]: res }));
    } catch (err) {
      console.error("submit quiz failed", err);
    }
  };

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Quiz" title="Quiz disponibles" description="Ils sont rendus à partir du JSON de quiz généré et des questions stockées, afin que les étudiants voient un vrai quiz au lieu de JSON brut." />

      <div className="grid gap-4 md:grid-cols-2">
        {availableQuizzesQuery.data?.map((quiz) => (
          <Card key={quiz.quiz_id}>
            <CardHeader>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <CardTitle>{quiz.title}</CardTitle>
                  <CardDescription>{quiz.chapter_title} · {quiz.lesson_title}</CardDescription>
                </div>
                <Badge variant="secondary">{quiz.questions.length} questions</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {quiz.questions.map((question, index) => (
                <div key={question.question_id ?? `${quiz.quiz_id}-${index}`} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <p className="font-medium text-slate-950">{index + 1}. {question.question}</p>
                  <div className="mt-3 grid gap-2">
                    {question.options.length > 0 ? question.options.map((option) => (
                      <label key={option} className="flex items-start gap-3 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700">
                        <input
                          type="radio"
                          name={`quiz-${quiz.quiz_id}-question-${question.question_id ?? index}`}
                          className="mt-1"
                          onChange={() => handleOptionChange(quiz.quiz_id, question.question_id ?? index, option)}
                          checked={(answers[quiz.quiz_id] ?? {})[String(question.question_id ?? index)] === option}
                        />
                        <span>{option}</span>
                      </label>
                    )) : <p className="text-sm text-slate-600">Question à réponse libre</p>}
                  </div>
                </div>
              ))}
              <div className="pt-2">
                <button className="rounded bg-sky-600 px-3 py-2 text-white" onClick={() => submitQuiz(quiz.quiz_id)}>Soumettre et voir la correction</button>
              </div>
              {results[quiz.quiz_id] ? (
                <div className="mt-4 rounded border p-3">
                  <p className="font-medium">Score: {results[quiz.quiz_id]?.score ?? "—"} / {results[quiz.quiz_id]?.total}</p>
                  <div className="mt-2 space-y-2">
                    {results[quiz.quiz_id]?.details.map((d) => (
                      <div key={d.question_id} className="rounded border bg-white p-2">
                        <p>Question {d.question_id}: {d.correct ? "Correct" : "Incorrect"}</p>
                        {d.explanation ? <p className="text-sm text-slate-600">Correction: {d.explanation}</p> : null}
                        {d.correct_answer ? <p className="text-sm text-slate-700">Réponse attendue: {d.correct_answer}</p> : null}
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </CardContent>
          </Card>
        ))}
      </div>

      <PageHeader eyebrow="Historique" title="Historique et résultats des quiz" description="Les quiz terminés apparaissent toujours ci-dessous pour le suivi de la progression." />

      <div className="grid gap-4 md:grid-cols-2">
        {quizzesQuery.data?.map((quiz: any, index) => (
          <Card key={`${quiz.quiz_id ?? index}`}>
            <CardHeader>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <CardTitle>{quiz.lesson_title ?? `Quiz ${quiz.quiz_id ?? index + 1}`}</CardTitle>
                  <CardDescription>{quiz.chapter_title ?? "Quiz terminé"}</CardDescription>
                </div>
                <Badge variant="secondary">Score {quiz.score ?? "—"}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-7 text-slate-700">Tentatives : {quiz.attempts ?? 0}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
