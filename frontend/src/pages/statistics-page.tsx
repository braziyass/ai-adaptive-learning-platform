import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/page-header";
import { useTeacherStatisticsQuery, useStudentCurrentLevelQuery, useStudentProgressQuery } from "@/lib/query-hooks";
import { getCurrentRole } from "@/lib/auth";
import { formatPercent } from "@/lib/format";
import { StatCard } from "@/components/common/stat-card";

export function StatisticsPage() {
  const role = getCurrentRole();
  const teacherStatsQuery = useTeacherStatisticsQuery();
  const studentLevelQuery = useStudentCurrentLevelQuery();
  const studentProgressQuery = useStudentProgressQuery();

  const completedLessons = studentProgressQuery.data?.filter((item) => item.completed).length ?? 0;
  const totalLessons = studentProgressQuery.data?.length ?? 0;
  const completionRate = totalLessons > 0 ? (completedLessons / totalLessons) * 100 : 0;

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Statistiques" title="Indicateurs d'apprentissage adaptatif" description="Cette vue s'adapte à votre rôle et résume les analyses les plus pertinentes déjà exposées par le backend." />

      {role === "teacher" ? (
        <div className="grid gap-4 md:grid-cols-3">
          <StatCard title="Étudiants" value={String(teacherStatsQuery.data?.total_students ?? 0)} description="Apprenants dans le périmètre de l'enseignant." />
          <StatCard title="Taux d'achèvement" value={formatPercent(teacherStatsQuery.data?.completion_rate ?? 0)} description="Taux de complétion des leçons dans la cohorte." />
          <StatCard title="Validation réussie" value={formatPercent(teacherStatsQuery.data?.validation_pass_rate ?? 0)} description="Taux de réussite aux tests de validation chez les apprenants." />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-3">
          <StatCard title="Niveau actuel" value={String(studentLevelQuery.data?.current_level ?? 0)} description="Votre niveau d'apprentissage actif." />
          <StatCard title="Leçons terminées" value={String(completedLessons)} description="Leçons marquées comme terminées dans votre suivi." />
          <StatCard title="Taux d'achèvement" value={formatPercent(completionRate)} description="Part des leçons terminées dans le programme actuel." />
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Notes</CardTitle>
          <CardDescription>L'interface reste connectée aux réponses API existantes, donc cette page reste utile même quand le backend évolue.</CardDescription>
        </CardHeader>
        <CardContent className="text-sm leading-7 text-slate-700">
            Les statistiques administrateur pourront être étendues avec le même schéma une fois que le backend exposera un point de terminaison analytique dédié.
        </CardContent>
      </Card>
    </div>
  );
}
