import { useState } from "react";
import { BookOpen, GraduationCap, TrendingUp } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/common/page-header";
import { StatCard } from "@/components/common/stat-card";
import { formatPercent } from "@/lib/format";
import { teacherApi } from "@/lib/api";
import { useTeacherStatisticsQuery, useTeacherStudentsQuery } from "@/lib/query-hooks";
import type { PlacementTestResult, TeacherProgressItem, ValidationTestResult } from "@/types/api";
import { useQuery } from "@tanstack/react-query";

export function TeacherDashboardPage() {
  const studentsQuery = useTeacherStudentsQuery();
  const statisticsQuery = useTeacherStatisticsQuery();
  const [selectedStudentId, setSelectedStudentId] = useState<number | null>(studentsQuery.data?.[0]?.student_id ?? null);

  const progressQuery = useQuery({ queryKey: ["teacher", "progress", selectedStudentId], queryFn: () => teacherApi.studentProgress(selectedStudentId as number), enabled: selectedStudentId !== null });
  const placementQuery = useQuery({ queryKey: ["teacher", "placement-result", selectedStudentId], queryFn: () => teacherApi.placementResult(selectedStudentId as number), enabled: selectedStudentId !== null });
  const validationQuery = useQuery({ queryKey: ["teacher", "validation-results", selectedStudentId], queryFn: () => teacherApi.validationResults(selectedStudentId as number), enabled: selectedStudentId !== null });

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Enseignant" title="Analytique pédagogique et progression des apprenants" description="Consultez les cohortes, examinez un étudiant et validez les résultats d'apprentissage depuis le backend." />

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard title="Étudiants" value={String(statisticsQuery.data?.total_students ?? studentsQuery.data?.length ?? 0)} description="Liste d'apprenants visible par l'enseignant." />
        <StatCard title="Leçons terminées" value={String(statisticsQuery.data?.total_completed_lessons ?? 0)} description="Nombre de leçons terminées dans la cohorte." />
        <StatCard title="Taux d'achèvement" value={formatPercent(statisticsQuery.data?.completion_rate ?? 0)} description="Efficacité de complétion parmi les apprenants assignés." />
        <StatCard title="Validation réussie" value={formatPercent(statisticsQuery.data?.validation_pass_rate ?? 0)} description="Taux de réussite aux évaluations de validation." />
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
        <Card>
          <CardHeader>
            <CardTitle>Étudiants</CardTitle>
            <CardDescription>Sélectionnez un apprenant pour inspecter la progression, le positionnement et les validations.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <Input placeholder="Rechercher par nom ou e-mail" onChange={() => undefined} />
            </div>
            <div className="space-y-2">
              {studentsQuery.data?.map((student) => (
                <button
                  type="button"
                  key={student.student_id}
                  onClick={() => setSelectedStudentId(student.student_id)}
                  className={`w-full rounded-2xl border px-4 py-3 text-left transition ${selectedStudentId === student.student_id ? "border-slate-950 bg-slate-950 text-white" : "border-slate-200 bg-white hover:bg-slate-50"}`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-medium">{student.first_name} {student.last_name}</p>
                      <p className="text-sm opacity-80">{student.email}</p>
                    </div>
                    <Badge variant={selectedStudentId === student.student_id ? "secondary" : "default"} className={selectedStudentId === student.student_id ? "bg-white text-slate-950" : ""}>
                      Niveau {student.current_level}
                    </Badge>
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Vue étudiant</CardTitle>
            <CardDescription>Données en temps réel pour l'étudiant sélectionné.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {placementQuery.data ? <PlacementPanel placement={placementQuery.data} /> : null}
            <div>
              <h3 className="font-display text-lg font-semibold">Progression</h3>
              <div className="mt-3 grid gap-3 md:grid-cols-2">
                {progressQuery.data?.map((item) => <ProgressTile key={`${item.lesson_id}-${item.chapter_id}`} item={item} />)}
              </div>
            </div>
            <div>
              <h3 className="font-display text-lg font-semibold">Résultats de validation</h3>
              <div className="mt-3 space-y-3">
                {validationQuery.data?.map((item) => <ValidationTile key={`${item.lesson_id}-${item.quiz_id}`} item={item} />)}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function PlacementPanel({ placement }: { placement: PlacementTestResult }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-slate-950 p-2 text-white"><GraduationCap className="h-4 w-4" /></div>
        <div>
          <p className="font-medium">Résultat de positionnement</p>
          <p className="text-sm text-slate-600">Niveau attribué {placement.assigned_level} à partir du score {placement.placement_score}</p>
        </div>
      </div>
    </div>
  );
}

function ProgressTile({ item }: { item: TeacherProgressItem }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-medium">{item.lesson_title}</p>
          <p className="mt-1 text-sm text-slate-600">{item.chapter_title} · Ordre {item.chapter_order}</p>
        </div>
        <Badge variant={item.completed ? "success" : "warning"}>{item.completed ? "Terminée" : "En cours"}</Badge>
      </div>
      <div className="mt-3 flex items-center gap-3 text-sm text-slate-600">
        <BookOpen className="h-4 w-4" /> Score {item.score ?? "—"} · Tentatives {item.attempts}
      </div>
    </div>
  );
}

function ValidationTile({ item }: { item: ValidationTestResult }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-medium">{item.lesson_title}</p>
          <p className="mt-1 text-sm text-slate-600">Niveau {item.level} · {item.chapter_title}</p>
        </div>
        <Badge variant={item.passed ? "success" : "destructive"}>{item.passed ? "Réussi" : "Échoué"}</Badge>
      </div>
      <div className="mt-3 flex items-center gap-3 text-sm text-slate-600">
        <TrendingUp className="h-4 w-4" /> Score {item.score ?? "—"} · Tentatives {item.attempts}
      </div>
    </div>
  );
}
