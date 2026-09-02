import { BookOpen, ClipboardCheck, Trophy } from "lucide-react";
import type { ComponentType } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/page-header";
import { StatCard } from "@/components/common/stat-card";
import { formatPercent } from "@/lib/format";
import { useStudentCompletedQuizzesQuery, useStudentCurrentLevelQuery, useStudentProfileQuery, useStudentProgressQuery, useStudentUnlockedLessonsQuery, useStudentValidationResultsQuery } from "@/lib/query-hooks";

export function StudentDashboardPage() {
  const profileQuery = useStudentProfileQuery();
  const levelQuery = useStudentCurrentLevelQuery();
  const progressQuery = useStudentProgressQuery();
  const lessonsQuery = useStudentUnlockedLessonsQuery();
  const quizzesQuery = useStudentCompletedQuizzesQuery();
  const validationQuery = useStudentValidationResultsQuery();

  const completedCount = progressQuery.data?.filter((item) => item.completed).length ?? 0;
  const totalLessons = progressQuery.data?.length ?? 0;
  const completionRate = totalLessons > 0 ? (completedCount / totalLessons) * 100 : 0;

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Étudiant" title={`Bienvenue, ${profileQuery.data?.first_name ?? "apprenant"}`} description="Suivez votre niveau, vos leçons débloquées, l'historique des quiz et les résultats de validation au même endroit." />

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard title="Niveau actuel" value={String(levelQuery.data?.current_level ?? profileQuery.data?.current_level ?? 0)} description="Votre niveau attribué à partir des résultats du test de positionnement." />
        <StatCard title="Achèvement" value={formatPercent(completionRate)} description="Part des leçons marquées comme terminées dans le programme actuel." />
        <StatCard title="Leçons débloquées" value={String(lessonsQuery.data?.length ?? 0)} description="Leçons actuellement disponibles à étudier." />
        <StatCard title="Résultats de validation" value={String(validationQuery.data?.length ?? 0)} description="Tentatives de test de validation renvoyées par l'API." />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Card>
          <CardHeader><CardTitle>Profil</CardTitle><CardDescription>Vue d'ensemble de votre compte synchronisé avec le backend.</CardDescription></CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            <InfoChip label="Nom" value={`${profileQuery.data?.first_name ?? ""} ${profileQuery.data?.last_name ?? ""}`.trim()} />
            <InfoChip label="E-mail" value={profileQuery.data?.email ?? "—"} />
            <InfoChip label="Score de positionnement" value={String(profileQuery.data?.placement_score ?? 0)} />
            <InfoChip label="ID étudiant" value={String(profileQuery.data?.id ?? 0)} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Résumé d'apprentissage</CardTitle><CardDescription>Indicateurs issus de votre progression et de vos évaluations.</CardDescription></CardHeader>
          <CardContent className="space-y-3">
            {progressQuery.data?.slice(0, 4).map((item) => <SummaryRow key={item.lesson_id} title={item.lesson_title} meta={`${item.chapter_title} · Attempt ${item.attempts}`} completed={item.completed} score={item.score} />)}
            {quizzesQuery.data?.slice(0, 4).map((item: any, index) => <SummaryRow key={`${item.quiz_id ?? index}`} title={item.lesson_title ?? `Quiz ${item.quiz_id ?? index + 1}`} meta={`${item.chapter_title ?? "Historique des quiz"}`} completed={true} score={item.score ?? null} />)}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader><CardTitle>Leçons débloquées</CardTitle><CardDescription>Contenu d'étude renvoyé par le backend.</CardDescription></CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            {lessonsQuery.data?.map((lesson) => (
              <article key={lesson.lesson_id} className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="font-display text-lg font-semibold">{lesson.lesson_title}</h3>
                    <p className="mt-1 text-sm text-slate-600">{lesson.chapter_title} · Ordre {lesson.chapter_order}</p>
                  </div>
                  <Badge variant={lesson.completed ? "success" : "warning"}>{lesson.completed ? "Terminée" : "Débloquée"}</Badge>
                </div>
                <p className="mt-4 line-clamp-6 text-sm leading-6 text-slate-700">{lesson.content}</p>
              </article>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Statistiques</CardTitle><CardDescription>Accès rapide aux indicateurs de quiz et de validation.</CardDescription></CardHeader>
          <CardContent className="space-y-4">
            <MetricLine icon={ClipboardCheck} label="Quiz terminés" value={String(quizzesQuery.data?.length ?? 0)} />
            <MetricLine icon={Trophy} label="Leçons terminées" value={String(completedCount)} />
            <MetricLine icon={BookOpen} label="Leçons débloquées" value={String(lessonsQuery.data?.length ?? 0)} />
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">Les résultats de validation sont disponibles dans la page dédiée Test de validation et sur ce tableau de bord.</div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function InfoChip({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{label}</p>
      <p className="mt-2 font-medium text-slate-950">{value || "—"}</p>
    </div>
  );
}

function SummaryRow({ title, meta, completed, score }: { title: string; meta: string; completed: boolean; score: number | null }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <div>
        <p className="font-medium">{title}</p>
        <p className="text-sm text-slate-600">{meta}</p>
      </div>
      <div className="flex items-center gap-2">
        <Badge variant={completed ? "success" : "warning"}>{completed ? "Terminée" : "Ouverte"}</Badge>
        <span className="text-sm text-slate-600">Score {score ?? "—"}</span>
      </div>
    </div>
  );
}

function MetricLine({ icon: Icon, label, value }: { icon: ComponentType<{ className?: string }>; label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white p-4">
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-slate-950 p-2 text-white"><Icon className="h-4 w-4" /></div>
        <span className="text-sm font-medium text-slate-700">{label}</span>
      </div>
      <span className="font-display text-lg font-semibold">{value}</span>
    </div>
  );
}
