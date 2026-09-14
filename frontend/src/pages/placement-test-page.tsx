import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/page-header";
import { useStudentPlacementTestQuery, useSubmitPlacementTestMutation } from "@/lib/query-hooks";
import type { PlacementTestSubmissionResult, QuizSubmissionRequest } from "@/types/api";

export function PlacementTestPage() {
  const testQuery = useStudentPlacementTestQuery();
  const submitTest = useSubmitPlacementTestMutation();
  const navigate = useNavigate();

  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [result, setResult] = useState<PlacementTestSubmissionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnswerChange = (questionId: number, value: string) => {
    setAnswers((current) => ({ ...current, [questionId]: value }));
  };

  const handleSubmit = async () => {
    if (!testQuery.data) {
      return;
    }
    setError(null);

    const unanswered = testQuery.data.questions.filter((question) => !answers[question.question_id]);
    if (unanswered.length > 0) {
      setError(`Veuillez répondre à toutes les questions (${unanswered.length} restante(s)).`);
      return;
    }

    const payload: QuizSubmissionRequest = {
      answers: testQuery.data.questions.map((question) => ({ question_id: question.question_id, answer: answers[question.question_id] })),
    };

    try {
      const submitted = await submitTest.mutateAsync(payload);
      setResult(submitted);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Impossible d'envoyer le test de positionnement.");
    }
  };

  if (testQuery.isLoading) {
    return (
      <div className="space-y-8">
        <PageHeader eyebrow="Test de positionnement" title="Chargement du test..." description="Merci de patienter pendant que nous préparons vos questions." />
      </div>
    );
  }

  if (testQuery.isError || !testQuery.data) {
    return (
      <div className="space-y-8">
        <PageHeader eyebrow="Test de positionnement" title="Test indisponible" description="Aucun test de positionnement n'est disponible pour le moment. Contactez votre administrateur." />
      </div>
    );
  }

  if (result) {
    return (
      <div className="space-y-8">
        <PageHeader
          eyebrow="Test de positionnement"
          title="Résultat"
          description="Votre niveau a été déterminé à partir de vos réponses. Vous pouvez maintenant accéder à votre tableau de bord."
        />
        <Card>
          <CardHeader>
            <CardTitle>Score : {result.score}/100</CardTitle>
            <CardDescription>{result.correct} bonne(s) réponse(s) sur {result.total}.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Badge variant="success" className="text-sm">Niveau attribué : {result.assigned_level}</Badge>
            <div className="space-y-3">
              {result.details.map((detail) => (
                <div key={detail.question_id} className="rounded-2xl border border-slate-200 bg-white p-4">
                  <p className="font-medium">{detail.correct ? "Correct" : "Incorrect"}</p>
                  {detail.correct_answer ? <p className="mt-1 text-sm text-slate-700">Réponse attendue : {detail.correct_answer}</p> : null}
                  {detail.explanation ? <p className="mt-1 text-sm text-slate-600">{detail.explanation}</p> : null}
                </div>
              ))}
            </div>
            <Button onClick={() => navigate("/student/dashboard")}>Accéder à mon tableau de bord</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Test de positionnement"
        title={testQuery.data.title}
        description="Répondez à toutes les questions pour déterminer votre niveau de départ. Ce test ne peut être passé qu'une seule fois."
      />

      <Card>
        <CardHeader>
          <CardTitle>{testQuery.data.subject}</CardTitle>
          <CardDescription>{testQuery.data.questions.length} question(s)</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {testQuery.data.questions.map((question, index) => (
            <div key={question.question_id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <p className="font-medium text-slate-950">{index + 1}. {question.question}</p>
              <div className="mt-3 grid gap-2">
                {question.options.length > 0 ? (
                  question.options.map((option) => (
                    <label key={option} className="flex items-start gap-3 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700">
                      <input
                        type="radio"
                        name={`placement-question-${question.question_id}`}
                        className="mt-1"
                        onChange={() => handleAnswerChange(question.question_id, option)}
                        checked={answers[question.question_id] === option}
                      />
                      <span>{option}</span>
                    </label>
                  ))
                ) : (
                  <input
                    type="text"
                    className="h-10 rounded-xl border border-slate-200 bg-white px-3 text-sm"
                    placeholder="Votre réponse"
                    value={answers[question.question_id] ?? ""}
                    onChange={(event) => handleAnswerChange(question.question_id, event.target.value)}
                  />
                )}
              </div>
            </div>
          ))}

          {error ? <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div> : null}

          <Button onClick={handleSubmit} disabled={submitTest.isPending}>
            {submitTest.isPending ? "Envoi en cours..." : "Soumettre le test"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
