import { useState } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/common/page-header";
import { useStudentAvailableValidationTestsQuery, useStudentValidationResultsQuery, useSubmitValidationTestMutation } from "@/lib/query-hooks";
import type { QuizSubmissionRequest, ValidationTestSubmissionResult } from "@/types/api";

export function ValidationTestPage() {
  const availableQuery = useStudentAvailableValidationTestsQuery();
  const historyQuery = useStudentValidationResultsQuery();
  const submitValidationTest = useSubmitValidationTestMutation();

  const [answers, setAnswers] = useState<Record<number, Record<number | string, string>>>({});
  const [results, setResults] = useState<Record<number, ValidationTestSubmissionResult | null>>({});
  const [error, setError] = useState<string | null>(null);

  const handleOptionChange = (quizId: number, questionId: number | string, value: string) => {
    setAnswers((prev) => ({ ...prev, [quizId]: { ...(prev[quizId] ?? {}), [questionId]: value } }));
  };

  const submitTest = async (quizId: number) => {
    setError(null);
    const byQuestion = answers[quizId] ?? {};
    const payload: QuizSubmissionRequest = { answers: Object.entries(byQuestion).map(([qid, val]) => ({ question_id: Number(qid), answer: val })) };
    try {
      const res = await submitValidationTest.mutateAsync({ quizId, payload });
      setResults((prev) => ({ ...prev, [quizId]: res }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Impossible d'envoyer le test de validation.");
    }
  };

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Test de validation"
        title="Test de validation du niveau actuel"
        description="Obtenez au moins 80% pour valider votre niveau et débloquer le niveau suivant."
      />

      {error ? <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div> : null}

      <div className="grid gap-4 md:grid-cols-2">
        {availableQuery.data?.length === 0 ? (
          <Card>
            <CardContent className="p-6 text-sm text-slate-600">
              Aucun test de validation n'est disponible pour votre niveau actuel pour le moment.
            </CardContent>
          </Card>
        ) : null}
        {availableQuery.data?.map((quiz) => {
          const result = results[quiz.quiz_id];
          return (
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
                            name={`validation-${quiz.quiz_id}-question-${question.question_id ?? index}`}
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
                <Button onClick={() => submitTest(quiz.quiz_id)} disabled={submitValidationTest.isPending}>
                  {submitValidationTest.isPending ? "Envoi en cours..." : "Soumettre et voir la correction"}
                </Button>

                {result ? (
                  <div className="mt-4 space-y-3 rounded-2xl border border-slate-200 bg-white p-4">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge variant={result.passed ? "success" : "destructive"}>{result.passed ? "Validé" : "Non validé"}</Badge>
                      <span className="font-medium">Score {result.score ?? "—"}/100</span>
                      <span className="text-sm text-slate-600">+{result.points_awarded} points</span>
                    </div>
                    {result.leveled_up ? (
                      <p className="text-sm font-medium text-emerald-700">Félicitations, vous êtes passé au niveau {result.new_level} !</p>
                    ) : !result.passed ? (
                      <p className="text-sm text-slate-600">Score insuffisant (minimum 80%). Vous pouvez réessayer.</p>
                    ) : null}
                    <div className="space-y-2">
                      {result.details.map((d) => (
                        <div key={d.question_id} className="rounded border bg-slate-50 p-2 text-sm">
                          <p>Question {d.question_id}: {d.correct ? "Correct" : "Incorrect"}</p>
                          {d.explanation ? <p className="text-slate-600">Correction : {d.explanation}</p> : null}
                          {d.correct_answer ? <p className="text-slate-700">Réponse attendue : {d.correct_answer}</p> : null}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}
              </CardContent>
            </Card>
          );
        })}
      </div>

      <PageHeader eyebrow="Historique" title="Historique des tests de validation" description="Toutes vos tentatives de validation de niveau." />

      <div className="grid gap-4 md:grid-cols-2">
        {historyQuery.data?.map((result) => (
          <Card key={`${result.lesson_id}-${result.quiz_id}`}>
            <CardHeader>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <CardTitle>{result.lesson_title}</CardTitle>
                  <CardDescription>{result.chapter_title} · Niveau {result.level}</CardDescription>
                </div>
                <Badge variant={result.passed ? "success" : "destructive"}>{result.passed ? "Réussi" : "Échoué"}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-7 text-slate-700">Score {result.score ?? "—"} · Tentatives {result.attempts}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
