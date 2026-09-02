import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/common/page-header";
import { useStudentValidationResultsQuery } from "@/lib/query-hooks";

export function ValidationTestPage() {
  const validationQuery = useStudentValidationResultsQuery();

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Test de validation" title="Résultats de validation" description="Consultez l'historique des résultats de validation renvoyés par le backend." />

      <div className="grid gap-4 md:grid-cols-2">
        {validationQuery.data?.map((result) => (
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
